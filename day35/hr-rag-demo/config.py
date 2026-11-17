from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_DIR = ROOT / "chroma_db"
COLLECTION_NAME = "uri_hr_recruitment_demo"
OLLAMA_URL = "http://localhost:11434"
EMBED_MODEL = "bge-m3"
CHAT_MODEL = "qwen2.5:3b"
CHUNK_SIZE = 1100       # characters; demo-friendly, not a universal optimum
CHUNK_OVERLAP = 180     # characters
TOP_K = 5
MAX_DISTANCE = 0.75    # cosine distance; tune on a labelled evaluation set
