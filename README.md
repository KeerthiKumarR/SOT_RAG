# Autonomous MirAI Student Policy Advisor

> Production-grade Retrieval-Augmented Generation (RAG) system for the **Mirai School of Technology (MSOT)** Student Policy Handbook 2026.

🌐 **Live Streamlit App**: [https://sot-rag-advisor.streamlit.app/](https://sot-rag-advisor.streamlit.app/)  
📂 **GitHub Repository**: [https://github.com/KeerthiKumarR/SOT_RAG](https://github.com/KeerthiKumarR/SOT_RAG)

---

## 📌 Project Overview
The **Autonomous MirAI Student Policy Advisor** is an autonomous question-answering assistant designed to answer student queries regarding:
- Attendance grading tiers and debarment rules
- Medical leave and duty leave regularisation procedures (7-day rule, escalation hierarchy)
- Examination malpractice (UFM) policies and revaluation timelines
- No Dues and admit card fee regulations
- Student Code of Conduct and disciplinary procedures
- Club formation, 40% batch support threshold, and event approval workflows

The assistant is strictly constrained against hallucinations. All answers are derived directly from the provided source document (`Mirai_SoT_Policy_Handbook_2026.pdf`). If an inquiry falls outside the handbook, the assistant politely declines.

---

## 🏗️ Architecture & Technology Stack

```
                               ┌──────────────────────────────────────────────┐
                               │   Mirai_SoT_Policy_Handbook_2026.pdf (16p)   │
                               └──────────────────────┬───────────────────────┘
                                                      │ PyPDFLoader
                                                      ▼
                               ┌──────────────────────────────────────────────┐
                               │  RecursiveCharacterTextSplitter (1000 / 200) │
                               └──────────────────────┬───────────────────────┘
                                                      │ GoogleGenerativeAIEmbeddings
                                                      ▼ (text-embedding-004)
                               ┌──────────────────────────────────────────────┐
                               │            ChromaDB Vector Store             │
                               └──────────────────────┬───────────────────────┘
                                                      ▲
                                                      │ MultiQueryRetriever
Student Question ─────────► [FastAPI /chat] ──────────┴────────► [ChatGoogleGenerativeAI (temp=0.0)]
                                                                           │
                                                                           ▼
                                                                Authoritative Factual Response
```

* **Data Pipeline**:
  - `PyPDFLoader`: Ingests the 16-page official handbook.
  - `RecursiveCharacterTextSplitter`: Chunks with `chunk_size=1000` and `chunk_overlap=200` to maintain policy context integrity.
  - `GoogleGenerativeAIEmbeddings`: Vectorizes text using `models/text-embedding-004`.
  - `ChromaDB`: Persistent local vector database.
* **Retrieval & Generation**:
  - `MultiQueryRetriever`: Rewrites and expands student queries to bridge the vocabulary gap between casual language and formal handbook terminology.
  - `ChatGoogleGenerativeAI`: Generates responses using `gemini-2.5-flash` with `temperature=0.0`.
  - **Guardrails**: System prompt restricts the LLM strictly to retrieved context.
* **Application Layer**:
  - `backend.py`: FastAPI asynchronous REST server exposing `/ingest` and `/chat`.
  - `frontend.py`: Streamlit chat UI with latency tracking, source citation inspects, and error handling.
  - `eval.py`: LLM-as-a-judge benchmarking script generating `rag_eval_scores.csv`.

---

## 📂 Project Structure

```bash
SOT_RAG/
├── backend.py                         # FastAPI backend service
├── frontend.py                        # Streamlit chat interface
├── eval.py                            # Automated LLM-as-a-Judge benchmark suite
├── generate_pdf.py                    # Generator for the official 16-page Policy Handbook PDF
├── Mirai_SoT_Policy_Handbook_2026.pdf # Official 16-page Student Policy Handbook
├── rag_eval_scores.csv                # Benchmark evaluation logs (Scores 1-5 & Reasoning)
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .env                               # Local environment configuration
└── README.md                          # Standard Operating Procedures & Documentation
```

---

## 🚀 Setup & Execution Guide

### 1. Prerequisites & Environment Setup
Clone the repository and navigate to the project root:
```bash
git clone <your-repo-url>
cd SOT_RAG
```

Create and activate a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```
Add your Google API key:
```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_google_api_key_here
CHROMA_PERSIST_DIR=./chroma_db
PDF_FILE_PATH=./Mirai_SoT_Policy_Handbook_2026.pdf
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
```

### 3. Generate & Ingest Policy Handbook
Generate the 16-page policy handbook PDF:
```bash
python3 generate_pdf.py
```

### 4. Run the Backend API (FastAPI)
Launch the FastAPI server:
```bash
python3 backend.py
# Or via uvicorn directly:
uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```
API docs will be live at: `http://127.0.0.1:8000/docs`

### 5. Run the Frontend Interface (Streamlit)
In a new terminal window:
```bash
streamlit run frontend.py
```
Open your browser at `http://localhost:8501`.

---

## 📡 API Endpoints Specification

### 1. Document Ingestion
* **Endpoint**: `POST /ingest`
* **Content-Type**: `multipart/form-data`
* **Parameters**: `file` (optional PDF upload; ingests default handbook if omitted)
* **Response**:
  ```json
  {
    "status": "success",
    "chunks_indexed": 16,
    "message": "Successfully ingested and indexed default handbook './Mirai_SoT_Policy_Handbook_2026.pdf' (16 chunks)."
  }
  ```

### 2. Policy Chat Inquiry
* **Endpoint**: `POST /chat`
* **Content-Type**: `application/json`
* **Payload**:
  ```json
  {
    "question": "I have 72% attendance. How many attendance marks will I get?"
  }
  ```
* **Response**:
  ```json
  {
    "question": "I have 72% attendance. How many attendance marks will I get?",
    "answer": "Based on the Academic Evaluation Policy (Attendance Tier System), attendance between 60% – 74.99% awards 4 marks. Therefore, with 72% attendance, you will receive 4 marks out of 10.",
    "sources": [
      {
        "page": 2,
        "content": "Standard Attendance Evaluation: Attendance carries a 10% weightage across all courses..."
      }
    ],
    "status": "success"
  }
  ```

---

## 🧪 Certification Audit & Evaluation Results

Run the automated LLM-as-a-judge benchmark pipeline:
```bash
python3 eval.py
```

The benchmark evaluates the 4 required test queries and saves the score logs to [`rag_eval_scores.csv`](file:///Users/keerthikumar/Desktop/collective/SOT_RAG/rag_eval_scores.csv):

| Query ID | Category | Question | Expected Outcome | Score (1-5) | Result Status |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **TEST_01** | Precision Verification | *I have 72% attendance. How many attendance marks will I get?* | Exactly 4 marks (tier 60%–74.99%) | **5 / 5** | ✅ Pass |
| **TEST_02** | Multi-Hop Reasoning | *I study at the Ratnam campus. I got sick and need medical leave. Who do I email and how many days do I have to submit my documents?* | Contact Yashaswini Ma'am within exactly 7 days | **5 / 5** | ✅ Pass |
| **TEST_03** | Process Verification | *We want to start a new Cybersecurity society under the Tech Club. Do we ask Management directly?* | Requires 40% batch support; submit to Faculty Coordinator first, not Management | **5 / 5** | ✅ Pass |
| **TEST_04** | Negative Constraint | *How much is the fine for smoking a cigarette on campus?* | Prohibited + Disciplinary Committee action; no monetary fine fabricated | **5 / 5** | ✅ Pass |

**Overall System Benchmark**: **5.00 / 5.00**
