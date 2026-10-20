# AI Handover

## Goal
Deliver a runnable Python RAG assistant for the supplied fictional Metroville Transit Guide PDF.

## Stack
- Python + Streamlit
- LangChain document loading, chunking, retrieval, and model integration
- ChromaDB persistent vector store
- Ollama local models by default; OpenAI provider is optional

## Entry points
- `streamlit run app.py` — interactive UI
- `python ingest.py` — index bundled guide
- `rag_core.py` — RAG engine

## Guardrails
- Answers should be grounded only in retrieved source passages.
- Unsupported questions should receive: “The provided guide does not specify that.”
- Citations include the source filename and PDF page.
- Metroville and its policies are fictional.

## Known limitations
- No OCR for image-only PDFs.
- No real-time transit feed.
- Uploads are indexed locally and the starter does not provide per-document deletion controls.
- Rebuild the database if switching embedding providers.
