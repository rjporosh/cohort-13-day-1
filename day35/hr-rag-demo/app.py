import streamlit as st
from rag import answer_question
from config import CHAT_MODEL, EMBED_MODEL, COLLECTION_NAME, DB_DIR
import chromadb

st.set_page_config(page_title="Local HR Policy RAG", page_icon="📚", layout="wide")
st.title("📚 Local HR Policy Assistant — RAG Demo")
st.caption("Ollama + ChromaDB | Local inference | Evidence-backed answers")

with st.sidebar:
    st.subheader("Runtime")
    st.write(f"**Chat model:** `{CHAT_MODEL}`")
    st.write(f"**Embedding model:** `{EMBED_MODEL}`")
    try:
        client = chromadb.PersistentClient(path=str(DB_DIR))
        collection = client.get_or_create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
        st.metric("Indexed chunks", collection.count())
    except Exception as exc:
        st.error(str(exc))
    st.info("To add or replace a PDF, put it in `data/` and run `python ingest.py --file data/your.pdf --reset`.")

st.markdown("Ask in English or Bangla. Example: **What are the seven stages of the hiring process?**")
question = st.text_area("Your question", placeholder="আমাদের hiring process-এর ধাপগুলো কী?", height=90)
if st.button("Ask HR Assistant", type="primary", disabled=not question.strip()):
    with st.spinner("Retrieving evidence and generating a grounded answer..."):
        try:
            response, hits = answer_question(question.strip())
            st.subheader("Answer")
            st.write(response)
            with st.expander("Inspect retrieved evidence (debug)", expanded=True):
                for i, hit in enumerate(hits, start=1):
                    meta = hit["metadata"]
                    st.markdown(f"**{i}. {meta['source']} — PDF page {meta['page']} — distance {hit['distance']:.3f}**")
                    st.write(hit["text"])
                    st.divider()
        except Exception as exc:
            st.error(f"Could not answer: {exc}")
            st.code("Check that Ollama is running, both models are pulled, and `python ingest.py` completed.")

st.caption("Demo note: this is a learning prototype, not an authoritative HR/legal system. Verify policy answers against the official source.")
