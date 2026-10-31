def fixed_size_chunking(text, chunk_size=200):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

# Read document
with open("sample_document.txt", "r", encoding="utf-8") as file:
    document = file.read()

# Apply chunking
chunks = fixed_size_chunking(document, chunk_size=200)

# Display results
for index, chunk in enumerate(chunks):
    print(f"\n--- Chunk {index + 1} ---")
    print(chunk)
    print("Characters:", len(chunk))
