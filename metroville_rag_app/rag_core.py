"""Grounded PDF RAG engine: LangChain + Chroma, with Ollama or OpenAI."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = Path(os.getenv("CHROMA_DIR", str(BASE_DIR / "chroma_db")))
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "metroville_knowledge")


def get_embeddings(provider: str | None = None):
    provider = (provider or os.getenv("EMBEDDING_PROVIDER", "ollama")).lower()
    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"))
    from langchain_ollama import OllamaEmbeddings
    return OllamaEmbeddings(
        model=os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )


def get_vectorstore(provider: str | None = None) -> Chroma:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
        embedding_function=get_embeddings(provider),
    )


def load_and_split_pdf(pdf_path: str | Path, chunk_size: int = 900, chunk_overlap: int = 150):
    """Load PDF pages and split them while preserving page/source metadata."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    pages = PyMuPDFLoader(str(pdf_path)).load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(pages)
    for chunk in chunks:
        chunk.metadata["source"] = pdf_path.name
        # PyMuPDFLoader uses zero-based page numbers.
        chunk.metadata["page"] = int(chunk.metadata.get("page", 0)) + 1
    return chunks


def index_pdf(pdf_path: str | Path, provider: str | None = None, chunk_size: int = 900, chunk_overlap: int = 150, source_name: str | None = None) -> int:
    chunks = load_and_split_pdf(pdf_path, chunk_size, chunk_overlap)
    if source_name:
        for chunk in chunks:
            chunk.metadata["source"] = source_name
    store = get_vectorstore(provider)
    # Stable IDs make re-indexing the same file replace, rather than duplicate, its chunks.
    import hashlib
    ids = []
    for i, doc in enumerate(chunks):
        digest = hashlib.sha256(f"{doc.metadata['source']}|{doc.metadata['page']}|{i}|{doc.page_content}".encode()).hexdigest()
        ids.append(digest)
    store.add_documents(chunks, ids=ids)
    return len(chunks)


def get_llm(provider: str | None = None, temperature: float = 0.0):
    provider = (provider or os.getenv("LLM_PROVIDER", "ollama")).lower()
    if provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
            temperature=temperature,
        )
    from langchain_ollama import ChatOllama
    return ChatOllama(
        model=os.getenv("OLLAMA_CHAT_MODEL", "llama3.2"),
        temperature=temperature,
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )


SYSTEM_PROMPT = """You are Metroville Transit Guide, a retrieval-grounded assistant.
Answer using ONLY the supplied context. The Metroville network and all details in this document are fictional.
If the context does not contain the answer, clearly say: 'The provided guide does not specify that.' Do not guess, use outside knowledge, or invent routes, fares, hours, policies, contact details, or live service status.
Be concise but useful. When the context contains relevant rules or exceptions, include them. Never imply that you checked live service alerts.
Cite factual claims with the provided source labels, e.g. [metroville_transit_guide.pdf, p. 4].
"""


def answer_question(question: str, provider: str | None = None, embedding_provider: str | None = None,
                    k: int = 5, history: list[tuple[str, str]] | None = None):
    store = get_vectorstore(embedding_provider)
    retriever = store.as_retriever(search_type="similarity", search_kwargs={"k": k})
    docs = retriever.invoke(question)
    if not docs:
        return "The provided guide does not specify that.", []

    context_parts = []
    for doc in docs:
        source = Path(str(doc.metadata.get("source", "unknown source"))).name
        page = doc.metadata.get("page", "?")
        context_parts.append(f"[Source: {source}, p. {page}]\n{doc.page_content}")
    context = "\n\n---\n\n".join(context_parts)

    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    # Keep only a small amount of prior conversation so follow-ups have context.
    for user_text, assistant_text in (history or [])[-4:]:
        messages.append(HumanMessage(content=user_text))
        messages.append(AIMessage(content=assistant_text))
    messages.append(HumanMessage(content=f"Retrieved context:\n{context}\n\nUser question: {question}"))
    response = get_llm(provider).invoke(messages)
    return str(response.content), docs


def source_label(doc) -> str:
    source = Path(str(doc.metadata.get("source", "unknown source"))).name
    page = doc.metadata.get("page", "?")
    return f"{source} · page {page}"
