"""
Autonomous MirAI Student Policy Advisor - Frontend UI
Streamlit Chat Application connecting to FastAPI RAG backend.
"""

import os
import time
import requests
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="MirAI Policy Advisor | MSOT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    backend_url = st.text_input(
        "Backend API URL",
        value=os.getenv("BACKEND_URL", "http://127.0.0.1:8000"),
        help="FastAPI server endpoint"
    )
    
    # Server Connection Check
    backend_online = False
    try:
        health_resp = requests.get(f"{backend_url}/health", timeout=2)
        if health_resp.status_code == 200:
            backend_online = True
            st.success("🟢 Backend Connected")
        else:
            st.warning("🟡 Backend unreachable")
    except Exception:
        st.error("🔴 Backend Offline")
    
    st.markdown("---")
    st.subheader("📄 Handbook Ingestion")
    uploaded_pdf = st.file_uploader("Upload New Handbook (PDF)", type=["pdf"])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ingest Upload", disabled=not uploaded_pdf or not backend_online, use_container_width=True):
            with st.spinner("Processing & indexing PDF..."):
                try:
                    files = {"file": (uploaded_pdf.name, uploaded_pdf.getvalue(), "application/pdf")}
                    res = requests.post(f"{backend_url}/ingest", files=files, timeout=60)
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"Indexed {data.get('chunks_indexed', 0)} chunks!")
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")
    
    with col2:
        if st.button("Index Default", disabled=not backend_online, use_container_width=True):
            with st.spinner("Indexing default handbook..."):
                try:
                    res = requests.post(f"{backend_url}/ingest", timeout=60)
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"Indexed {data.get('chunks_indexed', 0)} chunks!")
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection failed: {str(e)}")

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
        
        if not backend_online:
            error_msg = "⚠️ **Backend Error**: Cannot reach the FastAPI server. Please make sure `backend.py` is running on `127.0.0.1:8000`."
            message_placeholder.markdown(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg, "sources": []})
        else:
            with st.spinner("Consulting Policy Handbook with MultiQuery Retrieval..."):
                start_time = time.time()
                try:
                    payload = {"question": prompt_to_process}
                    response = requests.post(f"{backend_url}/chat", json=payload, timeout=45)
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "No answer returned.")
                        sources = data.get("sources", [])
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
                    else:
                        err_text = f"❌ Server returned error ({response.status_code}): {response.text}"
                        message_placeholder.markdown(err_text)
                        st.session_state.messages.append({"role": "assistant", "content": err_text, "sources": []})
                except requests.exceptions.Timeout:
                    timeout_msg = "⏳ **Request Timeout**: The backend took too long to respond. Please try again."
                    message_placeholder.markdown(timeout_msg)
                    st.session_state.messages.append({"role": "assistant", "content": timeout_msg, "sources": []})
                except Exception as e:
                    err_msg = f"❌ **Error connecting to advisor backend**: {str(e)}"
                    message_placeholder.markdown(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg, "sources": []})
