import argparse
import os
import re
from pathlib import Path
import chromadb
from docx import Document
from openai import OpenAI

BASE = Path(__file__).resolve().parent
POLICY = BASE / "data" / "HR_Policy.docx"
DB_PATH = BASE / "chroma_db"
COLLECTION = "hr_policy_handbook"
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
openai_client = OpenAI()
chroma = chromadb.PersistentClient(path=str(DB_PATH))


def extract_pages():
    doc = Document(POLICY)
    pages, current_page, current_lines = [], 1, []
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        match = re.search(r"PAGE\s+(\d{2})\s+OF\s+20", text)
        if match:
            if current_lines:
                pages.append((current_page, " ".join(current_lines)))
                current_lines = []
            current_page = int(match.group(1))
        else:
            current_lines.append(text)
    if current_lines:
        pages.append((current_page, " ".join(current_lines)))
    return pages

def split_into_chunks(text, size=1000, overlap=150):
    text = re.sub(r"\s+", " ", text).strip()
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind(". ", start + int(size * 0.65), end)
            if boundary > start:
                end = boundary + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks

def index_policy():
    if not POLICY.exists():
        raise FileNotFoundError(f"Cannot find policy document: {POLICY}")
    chunks = []
    for page, text in extract_pages():
        for chunk_no, chunk in enumerate(split_into_chunks(text)):
            chunks.append({"text": chunk, "page": page, "page_chunk": chunk_no})
    try:
        chroma.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = chroma.create_collection(
        name=COLLECTION, metadata={"hnsw:space": "cosine"}
    )
    print(f"Extracted pages: {len(extract_pages())}")
    print(f"Chunks created: {len(chunks)}")
    print("Generating embeddings and storing vectors in local ChromaDB...")
    batch_size = 64
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]
        texts = [x["text"] for x in batch]
        response = openai_client.embeddings.create(model=EMBED_MODEL, input=texts)
        vectors = [item.embedding for item in response.data]
        ids = [f"hr-chunk-{start+i:04d}" for i in range(len(batch))]
        metadata = [{"page": x["page"], "chunk_index": start+i}
                    for i, x in enumerate(batch)]
        collection.add(ids=ids, documents=texts, embeddings=vectors, metadatas=metadata)
        print(f"Stored {min(start + batch_size, len(chunks))}/{len(chunks)} chunks")
    print(f"\nDone. ChromaDB path: {DB_PATH}")
    print(f"Collection: {COLLECTION} | Stored vectors: {collection.count()}")

def retrieve(question, top_k=4):
    collection = chroma.get_or_create_collection(
        name=COLLECTION, metadata={"hnsw:space": "cosine"}
    )
    if collection.count() == 0:
        raise RuntimeError("Vector DB is empty. First run: python app.py index")
    embedding = openai_client.embeddings.create(
        model=EMBED_MODEL, input=question
    ).data[0].embedding
    result = collection.query(
        query_embeddings=[embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )
    return [
        {"text": text,
         "page": result["metadatas"][0][i]["page"],
         "distance": result["distances"][0][i]}
        for i, text in enumerate(result["documents"][0])
    ]

def ask(question, top_k=4):
    hits = retrieve(question, top_k)
    print("\n" + "=" * 68 + "\nRETRIEVED CHUNKS FROM CHROMADB\n" + "=" * 68)
    for i, hit in enumerate(hits, 1):
        print(f"\n[Chunk {i} | HR Policy page {hit['page']} | distance={hit['distance']:.4f}]")
        print(hit["text"])
    context = "\n\n".join(
        f"[Source: HR Policy page {h['page']}]\n{h['text']}" for h in hits
    )
    response = openai_client.responses.create(
        model=CHAT_MODEL,
        instructions=(
            "You are an HR policy assistant. Answer using only the retrieved "
            "excerpts. Do not invent rules. If they do not answer the question, "
            "say the excerpts do not provide enough information. Cite pages "
            "like [HR Policy, page 12]."
        ),
        input=f"Retrieved excerpts:\n{context}\n\nEmployee question: {question}\n"
              "Answer clearly and cite relevant page number(s).",
    )
    print("\n" + "=" * 68 + "\nLLM RESPONSE\n" + "=" * 68)
    print(response.output_text)

def main():
    parser = argparse.ArgumentParser(description="HR Policy RAG demo")
    subs = parser.add_subparsers(dest="command")
    subs.add_parser("index", help="Chunk, embed, and store the policy")
    ask_parser = subs.add_parser("ask", help="Ask a policy question")
    ask_parser.add_argument("question", nargs="?", help="Question to ask")
    ask_parser.add_argument("--top-k", type=int, default=4)
    args = parser.parse_args()
    if args.command == "index":
        index_policy()
    elif args.command == "ask":
        question = args.question or input("Ask an HR policy question: ").strip()
        if question:
            ask(question, args.top_k)
    else:
        question = input("Ask an HR policy question: ").strip()
        if question:
            ask(question)

if __name__ == "__main__":
    main()
