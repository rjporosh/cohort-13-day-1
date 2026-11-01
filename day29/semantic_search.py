
import os
import json
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer


# ==========================================
# 1. KNOWLEDGE BASE (DOCUMENT CHUNKS)
# ==========================================

chunks = [
    "Students can reset their university email password through the Student Portal.",
    "The university provides free Wi-Fi in all academic buildings and libraries.",
    "Students can access licensed software such as Microsoft 365 using their university email.",
    "For internet connectivity problems, students should contact the IT Helpdesk.",
    "The IT Helpdesk operates from Sunday to Thursday, 9 AM to 5 PM.",
    "Students must use Multi-Factor Authentication (MFA) to access university systems."
]


# ==========================================
# 2. SAMPLE QUESTIONS
# ==========================================

questions = [
    "How can I get Microsoft Office for free?",
    "How do I secure my university account?",
    "I forgot my email password. How can I recover it?",
    "Who should I contact if the internet is not working?",
    "Where can I use wireless internet on campus?"
]


# ==========================================
# 3. CONFIGURATION
# ==========================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

INDEX_FILE = "university_faiss.index"
CHUNKS_FILE = "document_chunks.json"

TOP_K = 3


# ==========================================
# 4. LOAD EMBEDDING MODEL
# ==========================================

print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

print("Model loaded successfully!")


# ==========================================
# 5. DOCUMENT EMBEDDING + INDEXING
# ==========================================

def create_document_index():

    print("\nCreating document embeddings...")

    # Generate document embeddings ONLY ONCE
    document_embeddings = model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    # FAISS requires float32 contiguous arrays
    document_embeddings = np.ascontiguousarray(
        document_embeddings,
        dtype=np.float32
    )

    # Get embedding dimension
    dimension = document_embeddings.shape[1]

    # Create FAISS index
    # Inner Product on normalized vectors = Cosine Similarity
    index = faiss.IndexFlatIP(dimension)

    # Add document vectors to FAISS
    index.add(document_embeddings)

    print(f"Total documents indexed: {index.ntotal}")

    # Persist index to disk
    faiss.write_index(index, INDEX_FILE)

    # Persist original chunks
    with open(CHUNKS_FILE, "w", encoding="utf-8") as file:
        json.dump(chunks, file, ensure_ascii=False, indent=4)

    print("FAISS index saved successfully!")

    return index


# ==========================================
# 6. LOAD EXISTING INDEX
# ==========================================

def load_or_create_index():

    if os.path.exists(INDEX_FILE) and os.path.exists(CHUNKS_FILE):

        print("\nLoading existing FAISS index...")

        index = faiss.read_index(INDEX_FILE)

        with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
            saved_chunks = json.load(file)

        if saved_chunks == chunks and index.ntotal == len(chunks):
            print("Existing index loaded. No document re-embedding!")
            return index

        print("Knowledge Base changed. Rebuilding index...")

    return create_document_index()


# ==========================================
# 7. SEMANTIC SEARCH
# ==========================================

def semantic_search(query, index, top_k=TOP_K):

    # Generate embedding ONLY for the user query
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = np.ascontiguousarray(
        query_embedding,
        dtype=np.float32
    )

    # Search FAISS index
    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        results.append({
            "chunk_id": int(idx),
            "document": chunks[idx],
            "similarity_score": float(score)
        })

    return results


# ==========================================
# 8. MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    # Build/load index ONCE, outside the question loop
    faiss_index = load_or_create_index()

    print("\n" + "=" * 65)
    print("UNIVERSITY IT HELPDESK - SEMANTIC SEARCH")
    print("=" * 65)

    # Search all sample questions
    for question_number, question in enumerate(questions, 1):

        print(f"\nQ{question_number}: {question}")
        print("-" * 65)

        results = semantic_search(
            query=question,
            index=faiss_index,
            top_k=TOP_K
        )

        for rank, result in enumerate(results, 1):

            print(f"\nRank: {rank}")
            print(f"Chunk ID: {result['chunk_id']}")
            print(f"Document: {result['document']}")
            print(
                f"Similarity Score: "
                f"{result['similarity_score']:.4f}"
            )

    print("\n" + "=" * 65)
    print("SEMANTIC SEARCH COMPLETED!")
    print("=" * 65)
