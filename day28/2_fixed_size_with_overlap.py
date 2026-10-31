def overlapping_chunking(text, chunk_size=200, overlap=50):

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size")
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # Move forward, keeping overlap
        start += chunk_size - overlap
    return chunks

# Read document
with open("sample_document.txt", "r", encoding="utf-8") as file:
    document = file.read()

# Apply chunking
chunks = overlapping_chunking(
    document,
    chunk_size=200,
    overlap=50
)

# Display results
for index, chunk in enumerate(chunks):
    print(f"\n--- Chunk {index + 1} ---")
    print(chunk)
    print("Characters:", len(chunk))