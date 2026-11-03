# pip install -U "qdrant-client[fastembed]" sentence-transformers
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding

# Step 1: Load Dense Embedding Model
dense_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Step 2: Load Sparse Embedding Model
sparse_model = SparseTextEmbedding(
    model_name="Qdrant/bm25"
)

# Step 3: Connect to Qdrant
client = QdrantClient(
    path="./qdrant_data"
)

collection_name = "hr_hybrid_policies"

# Step 4: Prepare documents
chunks = [
    {
        "id": 101,
        "section": "Working Hours",
        "content": "Employees are expected to work from Sunday to Thursday. Regular office hours are from 9 AM to 6 PM."
    },
    {
        "id": 102,
        "section": "Leave Policy",
        "content": "Employees in grade G7 are eligible for 25 days of annual leave. Employees in grade G5 are eligible for 20 days of annual leave."
    },
    {
        "id": 103,
        "section": "Remote Work",
        "content": "Employees may work remotely with prior approval from their reporting manager."
    },
    {
        "id": 104,
        "section": "Sick Leave",
        "content": "Employees can take sick leave when they are medically unfit to work. Medical documentation may be required."
    }
]

texts = [chunk["content"] for chunk in chunks]

# Step 5: Generate Dense Embeddings
dense_embeddings = dense_model.encode(
    texts,
    normalize_embeddings=True
)

# Step 6: Generate Sparse Embeddings
sparse_embeddings = list(
    sparse_model.passage_embed(texts)
)

# Step 7: Recreate Qdrant Collection
if client.collection_exists(collection_name):
    client.delete_collection(collection_name)

client.create_collection(
    collection_name=collection_name,
    vectors_config={
        "dense": models.VectorParams(
            size=384,
            distance=models.Distance.COSINE
        )
    },
    sparse_vectors_config={
        "sparse": models.SparseVectorParams()
    }
)

# Step 8: Create Qdrant Points
points = []

for chunk, dense_vector, sparse_vector in zip(
    chunks,
    dense_embeddings,
    sparse_embeddings
):
    points.append(
        models.PointStruct(

            id=chunk["id"],
            vector={
                "dense": dense_vector.tolist(),
                "sparse": models.SparseVector(
                    indices=sparse_vector.indices.tolist(),
                    values=sparse_vector.values.tolist()
                )
            },

            payload={
                "section": chunk["section"],
                "content": chunk["content"]
            }
        )
    )

# Step 9: Insert Points
client.upsert(
    collection_name=collection_name,
    points=points
)

print("Hybrid Index created successfully!")
print("Total points:", len(points))
client.close()
