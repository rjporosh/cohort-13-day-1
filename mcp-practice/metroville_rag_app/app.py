from __future__ import annotations

import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from rag_core import DATA_DIR, answer_question, get_vectorstore, index_pdf, load_and_split_pdf, source_label

load_dotenv()
st.set_page_config(page_title="Metroville RAG Assistant", page_icon="🚇", layout="wide")

st.title("🚇 Metroville Transit — RAG Assistant")
st.caption("A complete retrieval-augmented generation demo powered by LangChain. Metroville is fictional; this is a practice project, not real travel advice.")

with st.sidebar:
    st.header("Model settings")
    llm_provider = st.selectbox("Chat model provider", ["ollama", "openai"], index=0,
                                 help="Ollama runs locally. OpenAI requires an API key in .env.")
    embedding_provider = st.selectbox("Embedding provider", ["ollama", "openai"], index=0)
    top_k = st.slider("Retrieved chunks", min_value=2, max_value=10, value=5)
    st.divider()
    st.subheader("Knowledge base")
    st.write("Default source: `data/metroville_transit_guide.pdf`")
    uploaded = st.file_uploader("Add another PDF", type=["pdf"])
    if st.button("Index uploaded PDF", disabled=uploaded is None, use_container_width=True):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.getvalue())
                tmp_path = Path(tmp.name)
            with st.spinner("Extracting, chunking, and embedding PDF…"):
                count = index_pdf(tmp_path, provider=embedding_provider, source_name=uploaded.name)
            # Preserve a friendly source name in metadata on subsequent uploads by using original filename.
            st.success(f"Indexed {count} chunks from {uploaded.name}.")
            st.rerun()
        except Exception as exc:
            st.error(f"Indexing failed: {exc}")
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
    if st.button("Index / refresh default guide", use_container_width=True):
        default_pdf = DATA_DIR / "metroville_transit_guide.pdf"
        try:
            with st.spinner("Indexing default guide…"):
                count = index_pdf(default_pdf, provider=embedding_provider)
            st.success(f"Indexed {count} chunks.")
        except Exception as exc:
            st.error(f"Indexing failed: {exc}")
    st.divider()
    st.markdown("**Local setup:** Ollama must be running and the selected models pulled. See README.md.")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "history_for_rag" not in st.session_state:
    st.session_state.history_for_rag = []

with st.expander("Try these questions", expanded=not st.session_state.messages):
    examples = [
        "How much is a standard adult fare, and how long do transfers last?",
        "Which stations have step-free access?",
        "Can I take a standard bicycle on the metro at 8 a.m. on a weekday?",
        "What is the lost-property retention period?",
        "Does the Day Pass cover the weekend ferry?",
        "What is the current Blue Line delay?",
    ]
    cols = st.columns(2)
    for i, example in enumerate(examples):
        if cols[i % 2].button(example, key=f"example_{i}", use_container_width=True):
            st.session_state.pending_question = example

for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])
        if item.get("sources"):
            with st.expander("Retrieved source passages"):
                for source in item["sources"]:
                    st.markdown(f"**{source['label']}**")
                    st.write(source["content"])

question = st.chat_input("Ask about fares, routes, accessibility, passes, or policies…")
if not question and st.session_state.get("pending_question"):
    question = st.session_state.pop("pending_question")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching the guide and preparing a grounded answer…"):
                answer, docs = answer_question(
                    question,
                    provider=llm_provider,
                    embedding_provider=embedding_provider,
                    k=top_k,
                    history=st.session_state.history_for_rag,
                )
            st.markdown(answer)
            source_items = [{"label": source_label(doc), "content": doc.page_content} for doc in docs]
            if source_items:
                with st.expander("Retrieved source passages"):
                    for source in source_items:
                        st.markdown(f"**{source['label']}**")
                        st.write(source["content"])
            st.session_state.messages.append({"role": "assistant", "content": answer, "sources": source_items})
            st.session_state.history_for_rag.append((question, answer))
        except Exception as exc:
            message = f"**Could not answer yet.** {exc}\n\nCheck your provider settings and follow the setup steps in README.md."
            st.error(message)
            st.session_state.messages.append({"role": "assistant", "content": message, "sources": []})

if st.session_state.messages:
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.history_for_rag = []
        st.rerun()
