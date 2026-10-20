"""Index the bundled Metroville PDF into the persistent Chroma database."""
import argparse
from pathlib import Path
from rag_core import DATA_DIR, index_pdf


def main():
    parser = argparse.ArgumentParser(description="Index a PDF for the Metroville RAG assistant")
    parser.add_argument("pdf", nargs="?", default=str(DATA_DIR / "metroville_transit_guide.pdf"), help="PDF file path")
    parser.add_argument("--embeddings", choices=["ollama", "openai"], default=None)
    parser.add_argument("--chunk-size", type=int, default=900)
    parser.add_argument("--chunk-overlap", type=int, default=150)
    args = parser.parse_args()
    count = index_pdf(Path(args.pdf), provider=args.embeddings, chunk_size=args.chunk_size, chunk_overlap=args.chunk_overlap)
    print(f"Done: indexed {count} chunks from {args.pdf}")


if __name__ == "__main__":
    main()
