# Local HR Policy RAG Demo (বাংলা গাইড)

এই project-এ একটি public university recruitment procedure-এর source-derived demo excerpt PDF index করা হয়। PDF একবার chunk + embedding করে local ChromaDB-তে persist হয়। এরপর প্রতিটি প্রশ্নে শুধু relevant chunks retrieve করে Ollama LLM-কে দেওয়া হয়। পুরো PDF প্রতিবার LLM-কে পাঠানো হয় না।

## 0) কী কী লাগবে

- Python 3.10+
- Ollama installed and running
- প্রায় 5–8 GB free disk (models অনুযায়ী বেশি লাগতে পারে)
- macOS / Linux / Windows (Python environment ঠিক থাকলে)

Default models:
- Chat: `qwen2.5:3b`
- Embedding: `bge-m3` (Bangla + English-এর জন্য multilingual embedding)

## 1) Ollama model download

```bash
ollama pull qwen2.5:3b
ollama pull bge-m3
ollama serve
```

যদি Ollama আগে থেকেই background service হিসেবে চলে, `ollama serve` আবার চালানোর প্রয়োজন নেই। অন্য terminal-এ:

```bash
ollama list
```

## 2) Project setup

Project folder-এ যান:

```bash
cd hr-rag-demo
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Windows PowerShell হলে activate:

```powershell
.venv\Scripts\Activate.ps1
```

## 3) একবার document ingest করুন

```bash
python ingest.py
```

এখানে যা হবে:

1. PDF থেকে page-by-page text extract হবে।
2. Text 1,100 character-এর chunk-এ ভাগ হবে; 180 character overlap থাকবে।
3. `bge-m3` দিয়ে প্রতিটি chunk-এর embedding তৈরি হবে।
4. Text + embedding + source filename + PDF page metadata ChromaDB-তে save হবে।
5. Database `chroma_db/` folder-এ persist হবে।

একই index থাকলে script আবার embedding তৈরি করবে না। Rebuild করতে:

```bash
python ingest.py --reset
```

নিজের PDF index করতে:

```bash
python ingest.py --file data/my_hr_policy.pdf --reset
```

## 4) App চালান

```bash
streamlit run app.py
```

Browser-এ Streamlit-এর local URL খুলবে (সাধারণত `http://localhost:8501`)। এরপর প্রশ্ন করুন:

- What are the seven stages of the hiring process?
- What form is required when requesting interviews?
- Can a candidate be rejected for lacking a preferred qualification?
- How long must vacancies be posted?
- What are the confidentiality rules?
- What is the exact salary range for a software engineer? (এই excerpt-এ নেই; assistant-এর abstain করা উচিত।)

## 5) Architecture

```text
OFFLINE / ONE-TIME INGESTION
PDF -> PyPDF -> Chunking -> Ollama bge-m3 -> ChromaDB (persistent)

EACH USER QUESTION
Question -> bge-m3 embedding -> Chroma similarity search (Top 5)
        -> distance threshold -> evidence-only prompt -> qwen2.5:3b
        -> answer + source filename + PDF page citations
```

## 6) গুরুত্বপূর্ণ tuning

`config.py`-তে:

- `CHUNK_SIZE`: chunk-এর character length; section boundary-aware chunking এই demo-র next upgrade।
- `CHUNK_OVERLAP`: adjacent chunk-এর shared characters।
- `TOP_K`: কয়টি chunk LLM-কে দেওয়া হবে।
- `MAX_DISTANCE`: cosine distance threshold। এটি universal value নয়; নিজের প্রশ্ন/উত্তরের labelled test set দিয়ে tune করতে হবে।

`temperature=0.1` hallucination কমাতে সহায়তা করতে পারে, কিন্তু guarantee নয়। Retrieval ভুল হলে LLM-ও ভুল evidence পেতে পারে। Production-এ hybrid search (BM25 + vector), reranker, document version filters, claim-level citation validation, prompt-injection defence এবং RAG evaluation যোগ করুন।

## 7) Demo document সম্পর্কে সতর্কতা

`data/URI_HR_Recruitment_Procedure_Demo_Excerpt.pdf` হলো University of Rhode Island-এর official 54-page procedure document থেকে তৈরি সংক্ষিপ্ত source-derived learning excerpt; এটি original full PDF নয়। Official source এবং পূর্ণ document:

https://web.uri.edu/policies/wp-content/uploads/sites/928/Procedures-for-Policy-on-Employee-RSH-20240627.pdf

এটি 2024-07-01 effective date-এর policy procedure। আইন/নীতি পরিবর্তিত হতে পারে। বাস্তব HR সিদ্ধান্তে official/current policy-ই যাচাই করবেন।
