# HR Policy RAG Demo

Pipeline: 20-page HR Policy DOCX -> text extraction -> chunking -> OpenAI embeddings -> local ChromaDB -> semantic retrieval -> OpenAI Responses API -> answer with page citations.

The handbook is fictional and for learning only, not legal advice.

## Windows PowerShell setup

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If your API key is not already configured:
```powershell
$env:OPENAI_API_KEY="your-api-key"
```

## Index the document
```powershell
python app.py index
```

## Ask questions
```powershell
python app.py ask "How should an employee report workplace harassment?"
python app.py ask "What should an employee do after clicking a suspicious phishing link?"
python app.py ask "How many days of annual leave do employees receive?"
python app.py ask --top-k 5 "What happens when an employee resigns?"
```

Or run `python app.py` for interactive mode. The application prints retrieved chunks before the LLM response.

Choices: ChromaDB local persistent vector store; `text-embedding-3-small` embeddings; `gpt-5-mini` answer model by default (override with `OPENAI_MODEL`); about 1,000 characters per chunk with 150-character overlap. Re-run `python app.py index` after editing the policy.

This is a learning baseline. Production HR use requires access controls, evaluation, monitoring, document versioning, secure handling of HR data, and legal review.
