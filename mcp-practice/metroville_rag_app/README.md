# Metroville Transit RAG Assistant

A complete PDF question-answering project built with **Python, Streamlit, LangChain, ChromaDB, and Ollama or OpenAI**. The bundled PDF is a fictional Metroville public-transit guide made for RAG practice.

## Features

- Reads the included PDF and other uploaded PDFs.
- Extracts PDF text, splits it into overlapping chunks, embeds chunks, and stores them in persistent ChromaDB.
- Retrieves relevant passages for each question and asks the selected LLM to answer only from those passages.
- Shows source passage text and page metadata to make answers inspectable.
- Has a strict prompt for unsupported questions; the model should say the guide does not specify the answer rather than inventing a fact.
- Supports local Ollama models or OpenAI API models.
- Streamlit chat UI, example questions, configurable retrieval count, and conversation history.

> This knowledge base is fictional. Do not use it for actual transit decisions. RAG reduces unsupported answers but does not guarantee perfect accuracy; inspect citations and retrieved passages.

## 1. Requirements

- Python 3.10 or newer (Python 3.11 is a safe default for broad package compatibility).
- macOS, Linux, or Windows.
- For local inference: [Ollama](https://ollama.com/) installed and running.
- For OpenAI inference: an OpenAI API key and internet access.

## 2. Create a virtual environment (macOS)

From this project folder in Terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Each time you reopen Terminal, activate it again with `source .venv/bin/activate`.

## 3A. Local model setup with Ollama (no paid API required)

Install Ollama from its official website, open/run Ollama, then in Terminal:

```bash
ollama pull llama3.2
ollama pull nomic-embed-text
ollama list
```

The chat model generates answers; the embedding model converts PDF chunks and questions into vectors. They are separate models, so pull both. On a Mac with limited memory, a smaller Ollama model may be more comfortable; set `OLLAMA_CHAT_MODEL` in `.env` to a model you have already pulled.

Create your local config:

```bash
cp .env.example .env
```

The defaults use Ollama for both chat and embeddings.

## 3B. OpenAI setup (alternative)

Copy `.env.example` to `.env`, then set:

```dotenv
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

Keep the API key private and do not commit `.env`. OpenAI API usage may incur charges. In the sidebar, you can also choose providers for a session; the corresponding models and credentials must be configured.

## 4. Index the bundled PDF

With the virtual environment active and the selected provider available:

```bash
python ingest.py
```

Or index another PDF:

```bash
python ingest.py /absolute/path/to/your-document.pdf
```

Use OpenAI embeddings explicitly if desired:

```bash
python ingest.py --embeddings openai
```

Indexing can take a little while on the first run. The vector database is stored under `chroma_db/` by default. Re-indexing a PDF adds/replaces chunk IDs for the same source; for a clean rebuild, stop the app and remove the local `chroma_db/` directory, then run ingestion again.

## 5. Run the app

```bash
streamlit run app.py
```

Streamlit prints a local URL, typically `http://localhost:8501`. Open it in your browser. Ask questions such as:

- How much is a standard adult fare?
- Which stations have step-free access?
- Can I take a standard bicycle at 8 a.m. on a weekday?
- Does the Day Pass cover the weekend ferry?
- What is the current Blue Line delay? (The guide has no live service data, so the answer should say it does not specify.)

If you get a collection-not-found/empty knowledge-base response, click **Index / refresh default guide** in the sidebar or run `python ingest.py` first.

## 6. How it works

1. **Load:** `PyMuPDFLoader` extracts PDF text page by page.
2. **Chunk:** `RecursiveCharacterTextSplitter` creates overlapping text chunks while retaining source/page metadata.
3. **Embed:** Ollama or OpenAI embeddings represent each chunk numerically.
4. **Store:** ChromaDB persists vectors on disk.
5. **Retrieve:** Similarity search selects the top-k passages for a question.
6. **Generate:** LangChain sends the question plus retrieved passages to the LLM with instructions to stay grounded and admit when the source lacks the answer.
7. **Inspect:** The UI exposes retrieved passages and page labels.

## Project structure

```text
metroville_rag_app/
├── app.py                         # Streamlit user interface
├── rag_core.py                    # Loading, chunking, vector store, retrieval, prompting
├── ingest.py                      # CLI ingestion utility
├── requirements.txt
├── .env.example
├── data/
│   └── metroville_transit_guide.pdf
├── chroma_db/                     # Created/filled at runtime (ignored by Git)
└── README.md
```

## Troubleshooting

- **`ollama` connection refused:** open Ollama and verify `ollama list` works.
- **Model not found:** pull the exact model name from `.env` (for example `ollama pull llama3.2`).
- **OpenAI authentication error:** verify `OPENAI_API_KEY` in `.env` and restart Streamlit.
- **Embedding dimension/provider mismatch:** use a fresh vector DB if you switch embedding providers. Stop Streamlit, delete `chroma_db/`, then re-index using the new provider.
- **Weak answers:** increase top-k a little, check that the PDF contains searchable text, or try smaller chunks (e.g. 650 characters with 100 overlap).
- **PDF is scanned images:** OCR is not enabled in this starter; OCR the document first or add an OCR pipeline.

## Important engineering notes

- The app is a learning-quality RAG baseline, not a production-secure service.
- The source PDF is treated as data, never as instructions to override the system prompt.
- Retrieved content can still be incomplete or misleading; check the shown passages.
- For production, add authentication, upload limits, file-type validation, document deletion/re-index management, structured logging, evaluation tests, and monitoring.
