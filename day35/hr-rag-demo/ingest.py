"""One-time (or repeatable) PDF ingestion into a persistent Chroma collection."""
import argparse
import hashlib
from pathlib import Path

import chromadb
from pypdf import PdfReader

from config import DATA_DIR, DB_DIR, COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP
from ollama_client import embed_texts


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    text = " ".join(text.split())
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end == len(text):
            break
        start = end - overlap
    return chunks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=str(DATA_DIR / "URI_HR_Recruitment_Procedure_Demo_Excerpt.pdf"))
    parser.add_argument("--reset", action="store_true", help="Delete and rebuild this demo collection")
    args = parser.parse_args()
    pdf_path = Path(args.file).expanduser().resolve()
    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    client = chromadb.PersistentClient(path=str(DB_DIR))
    if args.reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", "description": "URI HR recruitment demo excerpt"},
    )
    if collection.count() and not args.reset:
        print(f"Index already contains {collection.count()} chunks. Skipping ingestion.")
        print("Use python ingest.py --reset to rebuild it.")
        return

    reader = PdfReader(str(pdf_path))
    records = []
    file_hash = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:16]
    for page_index, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        for chunk_index, chunk in enumerate(chunk_text(page_text)):
            chunk_id = f"{file_hash}-p{page_index}-c{chunk_index}"
            records.append({
                "id": chunk_id,
                "text": chunk,
                "metadata": {
                    "source": pdf_path.name,
                    "page": page_index,
                    "chunk": chunk_index,
                    "document_hash": file_hash,
                },
            })

    if not records:
        raise SystemExit("No extractable text found. This demo expects a text-based PDF, not a scanned image PDF.")

    batch_size = 32
    for offset in range(0, len(records), batch_size):
        batch = records[offset:offset + batch_size]
        vectors = embed_texts([r["text"] for r in batch])
        collection.add(
            ids=[r["id"] for r in batch],
            documents=[r["text"] for r in batch],
            metadatas=[r["metadata"] for r in batch],
            embeddings=vectors,
        )
        print(f"Indexed {min(offset + len(batch), len(records))}/{len(records)} chunks")

    print(f"Done. Indexed {collection.count()} chunks from {pdf_path.name}")
    print(f"Persistent DB: {DB_DIR}")


if __name__ == "__main__":
    main()
