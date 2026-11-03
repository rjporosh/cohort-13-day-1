
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding


# Step 1: Load models
dense_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

sparse_model = SparseTextEmbedding(
    model_name="Qdrant/bm25"
)


# Step 2: Connect to Qdrant
client = QdrantClient(
    path="./qdrant_data"
)

collection_name = "hr_hybrid_policies"

# Step 3: User question
question = "What is the annual leave entitlement for grade G7?"

# Step 4: Generate Dense Query Vector
dense_query = dense_model.encode(
    question,
    normalize_embeddings=True
).tolist()


# Step 5: Generate Sparse Query Vector
sparse_query = list(
    sparse_model.query_embed(question)
)[0]


# Step 6: Create Sparse Query
sparse_query_vector = models.SparseVector(
    indices=sparse_query.indices.tolist(),
    values=sparse_query.values.tolist()
)


# Step 7: Execute Hybrid Search
response = client.query_points(
    collection_name=collection_name,
    prefetch=[
        models.Prefetch(
            query=dense_query,
            using="dense",
            limit=4
        ),
        models.Prefetch(
            query=sparse_query_vector,
            using="sparse",
            limit=4
        )

    ],

    query=models.FusionQuery(
        fusion=models.Fusion.RRF # Reciprocal Rank Fusion
    ),
    limit=3,
    with_payload=True
)

# Step 8: Display results
print("\nUser Question:", question)
print("\nHybrid Search Results:")
for rank, point in enumerate(
    response.points,
    start=1
):
    print(f"\nRank: {rank}")
    print("Point ID:", point.id)
    print("RRF Score:", round(point.score, 4))
    print("Section:", point.payload["section"])
    print("Content:", point.payload["content"])

client.close()
