
# Required packages:
# pip install numpy faiss-cpu sentence-transformers

import numpy as np
import faiss

from sentence_transformers import SentenceTransformer


# ==================================================
# STEP 1: LOAD EMBEDDING MODEL
# ==================================================

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ==================================================
# STEP 2: DEFINE DOCUMENT CHUNKS
# ==================================================

chunks = [
    "Students can reset their university email password through the Student Portal.",

    "The university provides free Wi-Fi in all academic buildings and libraries.",

    "Students can access licensed software such as Microsoft 365 using their university email.",

    "For internet connectivity problems, students should contact the IT Helpdesk.",

    "The IT Helpdesk operates from Sunday to Thursday, 9 AM to 5 PM.",

    "Students must use Multi-Factor Authentication (MFA) to access university systems."
]


# ==================================================
# STEP 3: GENERATE DOCUMENT EMBEDDINGS
# ==================================================

print("\nGenerating document embeddings...")

chunk_embeddings = model.encode(
    chunks,
    convert_to_numpy=True
)

# Convert to float32 for FAISS
chunk_embeddings = np.asarray(
    chunk_embeddings,
    dtype=np.float32
)

print("Document Embeddings Shape:", chunk_embeddings.shape)
print("Vector Dimensions:", chunk_embeddings.shape[1])


# ==================================================
# STEP 4: NORMALIZE DOCUMENT VECTORS
# ==================================================

# Cosine Similarity = Dot Product of normalized vectors

document_norms = np.linalg.norm(
    chunk_embeddings,
    axis=1,
    keepdims=True
)

chunk_embeddings = chunk_embeddings / document_norms

print("\nDocument vectors normalized successfully!")


# ==================================================
# STEP 5: CREATE FAISS INDEX
# ==================================================

dimension = chunk_embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

# Add document embeddings to FAISS
index.add(chunk_embeddings)

print("\nTotal vectors in FAISS index:", index.ntotal)


# ==================================================
# STEP 6: DEFINE SAMPLE QUESTIONS
# ==================================================

questions = [
    "How can I get Microsoft Office for free?",

    "How do I secure my university account?",

    "I forgot my email password. How can I recover it?",

    "Who should I contact if the internet is not working?",

    "Where can I use wireless internet on campus?"
]


# ==================================================
# STEP 7: SEMANTIC SEARCH USING FAISS
# ==================================================

top_k = 3

for question_number, user_question in enumerate(
    questions,
    start=1
):

    print("\n" + "=" * 75)
    print(f"QUESTION {question_number}: {user_question}")
    print("=" * 75)

    # Generate query embedding
    query_embedding = model.encode(
        [user_question],
        convert_to_numpy=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    # Normalize query vector
    query_norm = np.linalg.norm(
        query_embedding,
        axis=1,
        keepdims=True
    )

    query_embedding = query_embedding / query_norm

    # ==================================================
    # STEP 8: CALCULATE COSINE SIMILARITY USING NUMPY
    # ==================================================

    numpy_scores = np.dot(
        query_embedding,
        chunk_embeddings.T
    )[0]

    # ==================================================
    # STEP 9: SEARCH USING FAISS
    # ==================================================

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    # ==================================================
    # STEP 10: DISPLAY TOP 3 RESULTS
    # ==================================================

    print("\nTop 3 Relevant Document Chunks:\n")

    for rank, (score, idx) in enumerate(
        zip(scores[0], indices[0]),
        start=1
    ):

        if idx == -1:
            continue

        print(f"Rank: {rank}")
        print(f"Chunk ID: {idx}")
        print(f"Similarity Score (FAISS): {score:.4f}")
        print(f"Similarity Score (NumPy): {numpy_scores[idx]:.4f}")
        print(f"Content: {chunks[idx]}")
        print("-" * 75)


# ==================================================
# STEP 11: COMPLETED
# ==================================================

print("\nSemantic Search Completed Successfully!")
print("Total Document Embeddings Generated: 6")
print("Total Documents Indexed:", index.ntotal)
print("Total Questions Processed:", len(questions))
