# HR RAG Local Demo --- macOS Setup Guide

এই README আপনার দেওয়া Terminal log এবং project-এর actual configuration
দেখে তৈরি। আপনার log-এ Python 3.14, macOS/Homebrew, `.venv`, ChromaDB,
Ollama এবং Streamlit ব্যবহার হয়েছে।

> **গুরুত্বপূর্ণ:** আপনার shell-এ `pip` alias `/opt/homebrew/bin/pip3`-এ
> point করছিল, কিন্তু Python virtual environment-এর ভিতরে ছিল। তাই
> `pip install` চালালে `externally-managed-environment` error হয়েছিল। এই
> project-এ package install করার জন্য সবসময়
> `./.venv/bin/python -m pip ...` ব্যবহার করুন।

## 1. Prerequisites

-   macOS with Homebrew
-   Python 3.14 (আপনার log-এ ব্যবহৃত)
-   Ollama
-   Project files: `app.py`, `ingest.py`, `rag.py`, `ollama_client.py`,
    `config.py`, `requirements.txt`
-   Demo PDF: `data/URI_HR_Recruitment_Procedure_Demo_Excerpt.pdf`

Project-এর `config.py` অনুযায়ী model names:

-   Chat model: `qwen2.5:3b`
-   Embedding model: `bge-m3`

## 2. Open Terminal and go to the project directory

আপনার Terminal log-এ project directory ছিল:

``` bash
cd ~/Downloads/porosh/cohort-13-practice/day35/hr-rag-demo
```

Directory ঠিক আছে কি না যাচাই করুন:

``` bash
pwd
ls
```

`app.py`, `ingest.py`, `requirements.txt` এবং `data/` দেখতে পাওয়ার কথা।

## 3. Create and activate the virtual environment

প্রথমবার project setup করার সময়:

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

Virtual environment active হয়েছে কি না যাচাই করুন:

``` bash
which python3
python3 --version
```

আপনার log-এ `python3` virtual environment-এর interpreter-এ resolve
হয়েছিল।

### Important: Avoid the Homebrew `pip` alias issue

আপনার shell-এ দেখা গিয়েছিল:

``` text
python: aliased to python3
python3: .../hr-rag-demo/.venv/bin/python3
pip: aliased to /opt/homebrew/bin/pip3
```

অর্থাৎ `python`/`python3` virtual environment ব্যবহার করলেও bare `pip`
Homebrew-এর global pip-এ চলে যাচ্ছিল। এই কারণে:

``` bash
pip install -r requirements.txt
```

চালালে `externally-managed-environment` error হয়েছিল।

**সঠিক ও নির্ভরযোগ্য পদ্ধতি:**

``` bash
./.venv/bin/python -m pip --version
```

এরপর package install করুন:

``` bash
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

আপনার দেওয়া log-এ এই exact installation command সফল হয়েছিল এবং প্রয়োজনীয়
packages install হয়েছিল।

> ভবিষ্যতেও `pip install ...`-এর বদলে
> `./.venv/bin/python -m pip install ...` ব্যবহার করুন। এতে shell alias বা
> PATH-এর কারণে ভুল Python environment-এ package install হওয়ার ঝুঁকি কমে।

## 4. Install and prepare Ollama models

Project configuration-এ Ollama server URL `http://localhost:11434` এবং
নিচের model names নির্ধারিত:

``` bash
ollama pull qwen2.5:3b
ollama pull bge-m3
```

Ollama model list যাচাই করুন:

``` bash
ollama list
```

Ollama service চালু না থাকলে আলাদা Terminal tab/window-তে চালান:

``` bash
ollama serve
```

যদি Ollama আগে থেকেই background service হিসেবে চলছে, দ্বিতীয়বার
`ollama serve` চালাবেন না।

**Note:** আপনার pasted Terminal log-এ `ollama pull` বা `ollama serve`
command-এর output ছিল না। তাই এগুলো project configuration অনুযায়ী প্রয়োজনীয়
setup command; pasted log থেকে এগুলো ইতিমধ্যে execute হয়েছিল বলে নিশ্চিত
হওয়া যাচ্ছে না।

## 5. Install Python dependencies

Project root directory-তে থেকে চালান:

``` bash
./.venv/bin/python -m pip install -r requirements.txt
```

Install verify করতে:

``` bash
./.venv/bin/python -m pip show chromadb pypdf requests streamlit
```

আপনার log-এ `chromadb`, `pypdf`, `requests` এবং `streamlit`-সহ
dependencies successfully install হয়েছিল।

## 6. Ingest the HR PDF --- one-time indexing

প্রথমবার document load, extract, chunk, embed এবং ChromaDB-তে persist
করতে:

``` bash
./.venv/bin/python ingest.py
```

আপনার actual output:

``` text
Indexed 8/8 chunks
Done. Indexed 8 chunks from URI_HR_Recruitment_Procedure_Demo_Excerpt.pdf
Persistent DB: .../hr-rag-demo/chroma_db
```

এর মানে demo PDF থেকে 8টি chunk তৈরি/index করা হয়েছিল এবং database
`chroma_db/` directory-তে persist হয়েছিল।

### What ingestion does

1.  PDF থেকে page-wise text extract করে।
2.  Extracted text ছোট ছোট chunk-এ ভাগ করে।
3.  Project-এর configured `bge-m3` embedding model দিয়ে chunk embedding
    তৈরি করে।
4.  Chunk text ও metadata ChromaDB collection-এ persist করে।
5.  পরবর্তী প্রশ্নে পুরো PDF পুনরায় embed না করে stored index থেকে relevant
    chunks retrieve করে।

এই project-এর `config.py`-তে:

``` python
CHUNK_SIZE = 1100
CHUNK_OVERLAP = 180
TOP_K = 5
MAX_DISTANCE = 0.75
```

এগুলো character-based chunking এবং retrieval configuration; এগুলো
universal optimum নয়।

### Rebuild/reset the index

আগের index মুছে নতুন করে ingestion করতে:

``` bash
./.venv/bin/python ingest.py --reset
```

আপনার log-এ এই command-ও সফল হয়েছিল:

``` text
Indexed 8/8 chunks
Done. Indexed 8 chunks from URI_HR_Recruitment_Procedure_Demo_Excerpt.pdf
```

**সাধারণ usage:** প্রথমবার `ingest.py` চালান। PDF বা ingestion
configuration পরিবর্তন করে index rebuild করতে হলে `--reset` ব্যবহার করুন।
প্রতিবার application চালানোর আগে reset করবেন না।

## 7. Run the Streamlit application

Project root directory-তে:

``` bash
./.venv/bin/python -m streamlit run app.py
```

আপনার log-এ `streamlit run app.py` command সফল হয়েছিল। Streamlit সাধারণত
browser-এ এই URL-এ app দেয়:

``` text
http://localhost:8501
```

আপনার actual output-এ ছিল:

``` text
Local URL: http://localhost:8501
Network URL: http://192.168.100.96:8501
```

Browser-এ `http://localhost:8501` খুলে HR document সম্পর্কে প্রশ্ন করুন।

## 8. Example questions

``` text
What are the seven stages of the hiring process?
What form is required when requesting interviews?
Can a candidate be rejected for lacking a preferred qualification?
How long must vacancies be posted?
What are the confidentiality requirements?
What is the salary range for a software engineer?
```

শেষ প্রশ্নটির উত্তর supplied excerpt-এ না থাকলে assistant-এর উচিত
unsupported salary range অনুমান না করে insufficient evidence জানানো।

## 9. Daily startup --- after initial setup

পরবর্তী সময়ে project চালাতে সাধারণত:

**Terminal 1 --- project environment and app**

``` bash
cd ~/Downloads/porosh/cohort-13-practice/day35/hr-rag-demo
source .venv/bin/activate
./.venv/bin/python -m streamlit run app.py
```

**Ollama:** Ollama background service চালু আছে কি না নিশ্চিত করুন। চালু না
থাকলে অন্য Terminal tab-এ:

``` bash
ollama serve
```

**Important:** Database আগে থেকেই তৈরি থাকলে প্রতিবার `ingest.py` চালানোর
প্রয়োজন নেই। `chroma_db/` persistent index হিসেবে থাকবে।

## 10. Troubleshooting

### A. `externally-managed-environment`

কারণ: bare `pip` Homebrew/global Python-এর pip-এ resolve করছে।

সমাধান:

``` bash
./.venv/bin/python -m pip install -r requirements.txt
```

`--break-system-packages` ব্যবহার করবেন না।

### B. Ollama connection refused

Ollama service চালু করুন:

``` bash
ollama serve
```

অন্য terminal-এ যাচাই করুন:

``` bash
ollama list
```

### C. Model not found

দুটি configured model pull করুন:

``` bash
ollama pull qwen2.5:3b
ollama pull bge-m3
```

### D. Streamlit command not found

Virtual environment-এর Python দিয়ে Streamlit চালান:

``` bash
./.venv/bin/python -m streamlit run app.py
```

### E. Rebuild the vector database

``` bash
./.venv/bin/python ingest.py --reset
```

## 11. Project architecture

``` text
ONE-TIME DOCUMENT INGESTION

HR PDF
  -> PyPDF text extraction
  -> Chunking
  -> Ollama bge-m3 embeddings
  -> ChromaDB persistent index


EACH USER QUESTION

User question
  -> Query embedding (bge-m3)
  -> ChromaDB similarity search
  -> Top-K relevant chunks
  -> Evidence-based prompt
  -> Ollama qwen2.5:3b
  -> Natural-language answer + source references
```

## 12. What was actually verified in the supplied Terminal log?

  ---------------------------------------------------------------------------------------------
  Operation                                                 Result in supplied log
  --------------------------------------------------------- -----------------------------------
  `python3 -m venv .venv`                                   Successful

  `source .venv/bin/activate`                               Successful

  `pip install -r requirements.txt`                         Failed due to global pip / PEP 668

  `./.venv/bin/python -m pip install -r requirements.txt`   Successful

  `python ingest.py`                                        Successful; 8/8 chunks indexed

  `python ingest.py --reset`                                Successful; 8/8 chunks indexed
                                                            again

  `streamlit run app.py`                                    Successful; local URL on port 8501

  `ollama pull` / `ollama serve`                            Not present in supplied log; see
                                                            model setup section
  ---------------------------------------------------------------------------------------------

## 13. Demo document

`data/URI_HR_Recruitment_Procedure_Demo_Excerpt.pdf` is a source-derived
learning excerpt based on the University of Rhode Island HR recruitment
procedure. It is not the complete original policy document. Verify the
current official policy before using it for real HR decisions.

Official source PDF:

https://web.uri.edu/policies/wp-content/uploads/sites/928/Procedures-for-Policy-on-Employee-RSH-20240627.pdf
