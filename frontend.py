import os
import time
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Attempt importing backend RAG modules for cloud standalone execution
DIRECT_RAG_AVAILABLE = False
try:
    import backend
    DIRECT_RAG_AVAILABLE = True
except Exception:
    pass

# Page Configuration
st.set_page_config(
    page_title="MirAI Policy Advisor | MSOT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Safely load Streamlit Secrets if available (on Streamlit Cloud)
try:
    if hasattr(st, "secrets"):
        if "GOOGLE_API_KEY" in st.secrets:
            os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
        if "GEMINI_API_KEY" in st.secrets:
            os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Custom CSS for rich modern aesthetic
st.markdown("""
<style>
    /* Theme styling */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .badge-primary {
        background-color: #0284c7;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .policy-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
    }
    .source-box {
        background: #f1f5f9;
        border-left: 3px solid #0284c7;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 0.85rem;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Application State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hello! I am the **MirAI Student Policy Advisor**. Ask me anything regarding academic evaluation, attendance tiers, leave regularisation, clubs, examination conduct, or grievances outlined in the **Mirai Student Policy Handbook 2026**.",
            "sources": []
        }
    ]

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/graduation-cap.png", width=64)
    st.title("Advisor Controls")
    
    # Server Connection Check
    backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    backend_online = False
    try:
        health_resp = requests.get(f"{backend_url}/health", timeout=1)
        if health_resp.status_code == 200:
            backend_online = True
    except Exception:
        backend_online = False
    
    if backend_online:
        st.success("🟢 FastAPI Backend Connected")
    elif DIRECT_RAG_AVAILABLE:
        st.success("🟢 Cloud Policy Engine Active")
    else:
        st.error("🔴 Backend Offline")
        
    with st.expander("⚙️ Connection Settings"):
        custom_url = st.text_input("Backend API URL", value=backend_url)
        backend_url = custom_url
    
    st.markdown("---")
    st.subheader("📄 Handbook Ingestion")
    uploaded_pdf = st.file_uploader("Upload New Handbook (PDF)", type=["pdf"])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ingest Upload", disabled=not uploaded_pdf, use_container_width=True):
            with st.spinner("Processing & indexing PDF..."):
                try:
                    if backend_online:
                        files = {"file": (uploaded_pdf.name, uploaded_pdf.getvalue(), "application/pdf")}
                        res = requests.post(f"{backend_url}/ingest", files=files, timeout=60)
                        if res.status_code == 200:
                            st.success(f"Indexed {res.json().get('chunks_indexed', 0)} chunks!")
                        else:
                            st.error(f"Error: {res.text}")
                    elif DIRECT_RAG_AVAILABLE:
                        import tempfile, shutil
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(uploaded_pdf.getvalue())
                            tmp_path = tmp.name
                        chunks_num = backend.process_pdf_and_vectorize(tmp_path)
                        st.success(f"Directly indexed {chunks_num} chunks!")
                except Exception as e:
                    st.error(f"Ingestion failed: {str(e)}")
    
    with col2:
        if st.button("Index Default", use_container_width=True):
            with st.spinner("Indexing default handbook..."):
                try:
                    if backend_online:
                        res = requests.post(f"{backend_url}/ingest", timeout=60)
                        if res.status_code == 200:
                            st.success(f"Indexed {res.json().get('chunks_indexed', 0)} chunks!")
                        else:
                            st.error(f"Error: {res.text}")
                    elif DIRECT_RAG_AVAILABLE:
                        chunks_num = backend.process_pdf_and_vectorize(backend.PDF_FILE_PATH)
                        st.success(f"Directly indexed {chunks_num} chunks!")
                except Exception as e:
                    st.error(f"Indexing failed: {str(e)}")

    st.markdown("---")
    st.subheader("🎯 Test Audit Queries")
    sample_queries = [
        "I have 72% attendance. How many attendance marks will I get?",
        "I study at the Ratnam campus. I got sick and need medical leave. Who do I email and how many days do I have to submit my documents?",
        "We want to start a new Cybersecurity society under the Tech Club. Do we ask Management directly?",
        "How much is the fine for smoking a cigarette on campus?"
    ]
    
    for sq in sample_queries:
        if st.button(f"📌 {sq[:38]}...", help=sq, use_container_width=True):
            st.session_state.pending_prompt = sq

    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

# Main Header
st.markdown('<div class="main-header">🎓 Autonomous MirAI Student Policy Advisor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Authoritative, hallucination-free policy assistance for Mirai School of Technology B.Tech students.</div>', unsafe_allow_html=True)

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("🔍 Retrieved Handbook Sources"):
                for idx, src in enumerate(msg["sources"]):
                    page_str = f"Page {src['page'] + 1}" if src.get("page") is not None else "Handbook Section"
                    st.markdown(f"**Source {idx+1} ({page_str}):**")
                    st.markdown(f"<div class='source-box'>{src['content']}</div>", unsafe_allow_html=True)

# Check for pending prompt from sample query buttons
prompt_to_process = None
if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    prompt_to_process = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

chat_input_val = st.chat_input("Ask a policy question (e.g. attendance criteria, leave rules, club formation)...")
if chat_input_val:
    prompt_to_process = chat_input_val

if prompt_to_process:
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt_to_process})
    with st.chat_message("user"):
        st.markdown(prompt_to_process)
    
    # Process Assistant Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        sources_placeholder = st.empty()
        
        with st.spinner("Consulting Policy Handbook with MultiQuery Retrieval..."):
            start_time = time.time()
            answer = ""
            sources = []
            
            # 1. Try FastAPI backend if online
            if backend_online:
                try:
                    payload = {"question": prompt_to_process}
                    response = requests.post(f"{backend_url}/chat", json=payload, timeout=45)
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "No answer returned.")
                        sources = data.get("sources", [])
                    else:
                        answer = f"❌ Server returned error ({response.status_code}): {response.text}"
                except Exception as e:
                    answer = f"❌ Error connecting to backend: {str(e)}"
            
            # 2. Fallback to Direct In-Process RAG (Streamlit Cloud mode)
            elif DIRECT_RAG_AVAILABLE:
                try:
                    if not os.path.exists(backend.CHROMA_PERSIST_DIR):
                        backend.process_pdf_and_vectorize(backend.PDF_FILE_PATH)
                    else:
                        backend.build_rag_pipeline()
                    
                    retrieved_docs = backend.multi_query_retriever.invoke(prompt_to_process)
                    sources = [
                        {"page": doc.metadata.get("page", None), "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content}
                        for doc in retrieved_docs
                    ]
                    raw_ans = backend.rag_chain.invoke(prompt_to_process)
                    if isinstance(raw_ans, list):
                        answer = "".join([str(c) if isinstance(c, str) else getattr(c, "text", str(c)) for c in raw_ans])
                    elif hasattr(raw_ans, "content"):
                        answer = str(raw_ans.content)
                    else:
                        answer = str(raw_ans)
                except Exception as e:
                    answer = f"❌ Error during direct RAG execution: {str(e)}"
            else:
                answer = "⚠️ **Backend Error**: Cannot reach FastAPI server on `127.0.0.1:8000` and direct pipeline is unavailable."

            elapsed = time.time() - start_time
            message_placeholder.markdown(answer)
            
            if sources:
                with sources_placeholder.expander(f"🔍 Retrieved Handbook Sources ({elapsed:.2f}s latency)"):
                    for idx, src in enumerate(sources):
                        page_str = f"Page {src['page'] + 1}" if src.get("page") is not None else "Handbook Section"
                        st.markdown(f"**Source {idx+1} ({page_str}):**")
                        st.markdown(f"<div class='source-box'>{src['content']}</div>", unsafe_allow_html=True)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources
            })
