# pip install qdrant-client sentence-transformers
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer

# Step 1: Load embedding model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Step 2: Define collection
collection_name = "hr_policies"

# Step 3: Connect to local Qdrant storage
client = QdrantClient(path="./qdrant_data")

# Step 4: Prepare document chunks and metadata
chunks = [
    {
        "id": 101,
        "department": "HR",
        "access_level": "Employee",
        "section": "Working Hours",
        "content": "Employees are expected to work from Sunday to Thursday. Regular office hours are from 9 AM to 6 PM."
    },
    {
        "id": 102,
        "department": "HR",
        "access_level": "HR Only",
        "section": "Salary Structure",
        "content": "The organization maintains salary grades based on employee roles and experience."
    },
    {
        "id": 103,
        "department": "HR",
        "access_level": "Employee",
        "section": "Leave Policy",
        "content": "Employees are entitled to annual leave, sick leave, and casual leave according to company policy."
    },
    {
        "id": 104,
        "department": "IT",
        "access_level": "Employee",
        "section": "Remote Work",
        "content": "Employees may work remotely with prior approval from their reporting manager."
    }
]

# Step 5: Generate embeddings
texts = [chunk["content"] for chunk in chunks]

embeddings = model.encode(
    texts,
    normalize_embeddings=True
)


# Step 6: Recreate collection for this demo
if client.collection_exists(collection_name):
    client.delete_collection(collection_name)

client.create_collection(
    collection_name=collection_name,
    vectors_config=models.VectorParams(
        size=384,
        distance=models.Distance.COSINE
    )
)

# Step 7: Convert chunks into Qdrant Points
points = []

for chunk, embedding in zip(chunks, embeddings):
    points.append(
        models.PointStruct(
            id=chunk["id"],
            vector=embedding.tolist(),
            payload={
                "department": chunk["department"],
                "access_level": chunk["access_level"],
                "section": chunk["section"],
                "content": chunk["content"]
            }
        )
    )

# Step 8: Insert points into Qdrant
client.upsert(
    collection_name=collection_name,
    points=points
)

print("Qdrant collection created successfully!")
print("Total points inserted:", len(points))

# Step 9: Close connection
client.close()
