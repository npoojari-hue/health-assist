# HealthAssist: A Consent-Based Health Habits Assistant

**Course:** COMP 4310 - Web Health Informatics, Lakehead University
**Team:** Code Health Crew - Nihar Poojari, Dinesh Reddy Morthala

HealthAssist is a web app for adults in Canada. After the user accepts a consent notice, they can enter a few everyday habits
(sleep, activity, sitting time). The app compares them with the Canadian 24-Hour Movement Guidelines using plain Python rules,
and answers general wellness questions using retrieval-augmented generation (RAG) over a small knowledge base of Canadian and WHO guidance.
Every answer shows its sources. It never diagnoses, it redirects medical and emergency questions, and it declines when the sources are not enough.

> This is a student prototype for general information only. It is not a medical device.

## Project structure
```
health-assist/
├── backend/app/        FastAPI app (main.py), safety.py, guidelines.py, rag.py, llm.py, pipeline.py,
│                       citations.py, crypto.py, database.py, schemas.py, config.py
├── frontend/           React (Vite) interface
├── data/knowledge_base/  approved source notes (TITLE / ORG / URL header + text)
├── scripts/ingest.py   rebuilds the ChromaDB index
├── tests/              pytest unit tests (rules, safety, citation check)
├── evaluation/         test_cases.json + run_eval.py (Llama vs Gemma, RAG vs no RAG)
└── docs/               P3 report and diagrams
```

## How to run
Requirements: Python 3.10+, Node 18+, [Ollama](https://ollama.com).

```bash
# 1. models (one time)
ollama pull llama3.1:8b
ollama pull gemma2:9b

# 2. backend (from the project root)
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.ingest                                 # build the vector index
uvicorn backend.app.main:app --reload                    # http://localhost:8000/docs

# 3. frontend (new terminal)
cd frontend && npm install && npm run dev                # http://localhost:5173
```

Rebuild the report PDF (project root): `python docs/make_diagrams.py && python docs/make_p3_pdf.py`
Run the tests: `python -m pytest`
Run the evaluation (Ollama must be running): `python -m evaluation.run_eval`

## Important notes
- The files in `data/knowledge_base/` are short paraphrased notes. Check them against the official pages (the URL is in each file header) before final submission.
- Hydration has no exact daily number in Canada's Food Guide, so it is answered by retrieval only and is not part of the rule-based comparison.
- Encryption protects data at rest, but it is not end-to-end encryption and it is not PIPEDA certification (see limitations in the report).
- Prototype limitation: one local user, no login.
- The first run of `python -m scripts.ingest` downloads a small embedding model (about 80 MB) for ChromaDB, so you need internet once.
- Tests use fake model/search responses, so `python -m pytest` runs without Ollama (21 tests).
