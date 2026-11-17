import requests
from config import OLLAMA_URL, EMBED_MODEL, CHAT_MODEL


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Create embeddings using Ollama's /api/embed endpoint."""
    response = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": texts},
        timeout=180,
    )
    response.raise_for_status()
    vectors = response.json().get("embeddings", [])
    if len(vectors) != len(texts):
        raise RuntimeError("Ollama returned an unexpected number of embeddings")
    return vectors


def generate_answer(prompt: str) -> str:
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": CHAT_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.1, "num_ctx": 8192},
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip()
