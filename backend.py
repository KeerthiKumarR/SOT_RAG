"""
Autonomous MirAI Student Policy Advisor - Backend API
FastAPI application implementing LCEL RAG pipeline with ChromaDB and Gemini.
"""

import os
import shutil
import tempfile
import warnings
from typing import List, Optional

warnings.filterwarnings("ignore", category=DeprecationWarning)
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LangChain and VectorStore imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
try:
    from langchain_classic.retrievers.multi_query import MultiQueryRetriever
except ImportError:
    try:
        from langchain.retrievers.multi_query import MultiQueryRetriever
    except ImportError:
        from langchain_community.retrievers.multi_query import MultiQueryRetriever

# Initialize FastAPI App
app = FastAPI(
    title="Autonomous MirAI Student Policy Advisor API",
    description="Production-grade RAG backend for MirAI Student Policy Handbook inquiries",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration Constants
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
PDF_FILE_PATH = os.getenv("PDF_FILE_PATH", "./Mirai_SoT_Policy_Handbook_2026.pdf")
DEFAULT_EMBEDDING_MODEL = "models/gemini-embedding-001"
DEFAULT_LLM_MODEL = "gemini-3.1-flash-lite"

# Global instances
vector_store: Optional[Chroma] = None
multi_query_retriever = None
rag_chain = None

def get_embeddings():
    """Initializes Google GenAI Embeddings with automatic model fallback."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.startswith("your_"):
        raise ValueError("Valid GOOGLE_API_KEY or GEMINI_API_KEY must be set in .env or Streamlit secrets.")
    embedding_model = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    return GoogleGenerativeAIEmbeddings(
        model=embedding_model,
        google_api_key=api_key
    )

def get_llm():
    """Initializes ChatGoogleGenerativeAI with temperature=0.0 for deterministic factual responses."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.startswith("your_"):
        raise ValueError("Valid GOOGLE_API_KEY or GEMINI_API_KEY must be set in .env or Streamlit secrets.")
    llm_model = os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL)
    return ChatGoogleGenerativeAI(
        model=llm_model,
        temperature=0.0,
        google_api_key=api_key
    )

def get_vector_store():
    """Loads existing ChromaDB vector store or initializes a new one."""
    global vector_store
    embeddings = get_embeddings()
    vector_store = Chroma(
        collection_name="mirai_policy_handbook",
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
    return vector_store

def build_rag_pipeline():
    """Builds the MultiQueryRetriever and LCEL RAG chain with guardrails."""
    global multi_query_retriever, rag_chain
    
    vs = get_vector_store()
    base_retriever = vs.as_retriever(search_kwargs={"k": 5})
    llm = get_llm()
    
    # Advanced Multi-Query Retriever to bridge vocabulary gap
    multi_query_retriever = MultiQueryRetriever.from_llm(
        retriever=base_retriever,
        llm=llm
    )
    
    # System Prompt with Strict Guardrails against hallucination
    system_prompt_template = """You are the official Autonomous MirAI Student Policy Advisor for Mirai School of Technology (MSOT).
Your duty is to provide authoritative, accurate, and helpful answers strictly based on the provided Mirai Student Policy Handbook context.

STRICT CONSTRAINTS & GUARDRAILS:
1. Rely ONLY on the clear facts stated directly in the retrieved context below.
2. If the user's question specifically asks about attendance marks or attendance tiers, cite the relevant bracket from the Standard Attendance Evaluation tier table (e.g. 60% – 74.99% awards 4 marks) and note the 75% debarment threshold. Do NOT include this table if the question is about unrelated topics like leave, clubs, or dress code.
3. DO NOT assume, extrapolate, speculate, or fabricate any rules, monetary amounts, penalties, or procedures not explicitly stated.
4. If the answer to a student's query cannot be found in the retrieved context, politely decline by stating: "I am sorry, but this information is not covered in the Mirai Student Policy Handbook. Please contact the Student Helpdesk at studenthelpdesk@msot.org or reach out to your Campus Manager for further guidance."
5. If a question asks about specific metrics (e.g. attendance percentage, deadlines, contacts, club formation thresholds), cite the exact figures and names from the policy (e.g., 7-day rule, 40% batch support, specific Campus Managers: Sundaram Sir for HI-Tech, Yashaswini Ma'am for Ratnam, Dolly Ma'am for JUJ).
6. Keep your answers concise, direct, and focused only on what the student asked.

Retrieved Policy Context:
{context}

Student Question:
{question}

Official Policy Advisor Answer:"""

    prompt = PromptTemplate(
        template=system_prompt_template,
        input_variables=["context", "question"]
    )
    
    def format_docs(docs):
        if not docs:
            return "No matching policy context found."
        formatted = []
        for i, doc in enumerate(docs):
            page_info = f"Page {doc.metadata.get('page', 'Unknown') + 1}" if 'page' in doc.metadata else "General Policy"
            formatted.append(f"[Document Chunk {i+1} | {page_info}]:\n{doc.page_content}")
        return "\n\n".join(formatted)

    rag_chain = (
        {"context": multi_query_retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

# Pydantic Request/Response Models
class ChatRequest(BaseModel):
    question: str = Field(..., description="Student inquiry regarding Mirai institutional policies", example="I have 72% attendance. How many attendance marks will I get?")

class SourceDocument(BaseModel):
    page: Optional[int] = None
    content: str

class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceDocument] = []
    status: str = "success"

class IngestResponse(BaseModel):
    status: str
    chunks_indexed: int
    message: str

@app.on_event("startup")
def startup_event():
    """Attempt initializing pipeline on startup if configuration exists."""
    try:
        if os.path.exists(PDF_FILE_PATH) and not os.path.exists(CHROMA_PERSIST_DIR):
            print("Auto-ingesting default PDF on startup...")
            process_pdf_and_vectorize(PDF_FILE_PATH)
        elif os.path.exists(CHROMA_PERSIST_DIR):
            build_rag_pipeline()
            print("Loaded existing ChromaDB vector store.")
    except Exception as e:
        print(f"Startup notice: Pipeline will be initialized on first /ingest or /chat call ({e})")

def process_pdf_and_vectorize(pdf_path: str) -> int:
    """Helper to process a PDF file, split into chunks, and store in ChromaDB."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")
    
    # 1. Ingestion using PyPDFLoader
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    if not documents:
        raise ValueError("Could not extract any content from the provided PDF.")
    
    # 2. Semantic Chunking with RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", "●", "•", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    # 3. Vector Database Storage in ChromaDB
    embeddings = get_embeddings()
    
    # Re-initialize collection
    global vector_store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="mirai_policy_handbook",
        persist_directory=CHROMA_PERSIST_DIR
    )
    
    build_rag_pipeline()
    return len(chunks)

@app.get("/")
def root():
    return {
        "service": "Autonomous MirAI Student Policy Advisor",
        "status": "online",
        "endpoints": {
            "ingest": "POST /ingest",
            "chat": "POST /chat",
            "health": "GET /health"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "chroma_dir_exists": os.path.exists(CHROMA_PERSIST_DIR),
        "pdf_exists": os.path.exists(PDF_FILE_PATH)
    }

@app.post("/ingest", response_model=IngestResponse)
async def ingest_pdf(file: Optional[UploadFile] = File(None)):
    """
    Accepts a PDF file via multipart/form-data, processes the chunks using
    RecursiveCharacterTextSplitter, and updates the local ChromaDB vector store.
    If no file is uploaded, falls back to the default handbook PDF.
    """
    try:
        if file and file.filename:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                shutil.copyfileobj(file.file, tmp)
                tmp_path = tmp.name
            try:
                num_chunks = process_pdf_and_vectorize(tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            return IngestResponse(
                status="success",
                chunks_indexed=num_chunks,
                message=f"Successfully ingested and indexed uploaded file '{file.filename}' into ChromaDB ({num_chunks} chunks)."
            )
        else:
            if not os.path.exists(PDF_FILE_PATH):
                raise HTTPException(status_code=400, detail=f"Default PDF not found at '{PDF_FILE_PATH}'. Please upload a PDF file.")
            num_chunks = process_pdf_and_vectorize(PDF_FILE_PATH)
            return IngestResponse(
                status="success",
                chunks_indexed=num_chunks,
                message=f"Successfully ingested and indexed default handbook '{PDF_FILE_PATH}' ({num_chunks} chunks)."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest PDF: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """
    Accepts a JSON payload containing the user's question, executes the
    MultiQueryRetriever + LCEL RAG chain, and returns the generated factual answer.
    """
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    try:
        global rag_chain, multi_query_retriever
        if rag_chain is None or multi_query_retriever is None:
            build_rag_pipeline()
            
        # Retrieve context documents via MultiQueryRetriever
        retrieved_docs = multi_query_retriever.invoke(payload.question)
        
        # Execute LCEL Chain
        raw_answer = rag_chain.invoke(payload.question)
        if isinstance(raw_answer, list):
            answer_parts = []
            for item in raw_answer:
                if isinstance(item, str):
                    answer_parts.append(item)
                elif isinstance(item, dict) and "text" in item:
                    answer_parts.append(item["text"])
                elif hasattr(item, "text"):
                    answer_parts.append(item.text)
                else:
                    answer_parts.append(str(item))
            answer = "".join(answer_parts).strip()
        elif hasattr(raw_answer, "content"):
            answer = str(raw_answer.content).strip()
        else:
            answer = str(raw_answer).strip()
        
        sources = [
            SourceDocument(
                page=doc.metadata.get("page", None),
                content=doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            )
            for doc in retrieved_docs
        ]
        
        return ChatResponse(
            question=payload.question,
            answer=answer,
            sources=sources,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing inquiry: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run("backend:app", host=host, port=port, reload=True)
