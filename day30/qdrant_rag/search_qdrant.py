
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer


# Step 1: Load embedding model
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Step 2: Connect to existing Qdrant storage
client = QdrantClient(path="./qdrant_data")
collection_name = "hr_policies"

# Step 3: Get user identity from backend
user_department = "IT"
user_access_level = "Employee"

# Step 4: User question
question = "What is the capital of Bangladesh?"

# Step 5: Generate query embedding
query_vector = model.encode(
    question,
    normalize_embeddings=True
).tolist()

# Step 6: Define metadata filter
query_filter = models.Filter(
    must=[
        models.FieldCondition(
            key="department",
            match=models.MatchValue(
                value=user_department
            )
        )
    ]
)

# Step 7: Search Qdrant
response = client.query_points(
    collection_name=collection_name,
    query=query_vector,
    query_filter=query_filter,
    limit=3,
    with_payload=True
)

# Step 8: Display results
print("\nUser Question:", question)
print("\nQdrant Search Results:")
for rank, point in enumerate(
    response.points,
    start=1
):

    print(f"\nRank: {rank}")
    print("Point ID:", point.id)
    print("Similarity Score:", round(point.score, 4))
    print("Department:", point.payload["department"])
    print("Section:", point.payload["section"])
    print("Content:", point.payload["content"])

# Step 9: Close connection
client.close()
