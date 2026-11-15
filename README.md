# HealthAssist: A Consent-Based Health Habits Assistant

**Course:** COMP 4310 - Web Health Informatics, Lakehead University
**Team:** Code Health Crew - Nihar Poojari, Dinesh Reddy Morthala

HealthAssist is a web app for adults in Canada. After the user accepts a consent notice, they can enter a few everyday habits
(sleep, activity, sitting time). The app compares them with the Canadian 24-Hour Movement Guidelines using plain Python rules,
and answers general wellness questions using retrieval-augmented generation (RAG) over a small knowledge base of Canadian and WHO guidance.
Every answer shows its sources. It never diagnoses, it redirects medical and emergency questions, and it declines when the sources are not enough.

> This is a student prototype for general information only. It is not a medical device.

## How it works
```
question -> safety filter -> retrieval (ChromaDB, distance <= 0.55) -> local LLM (Ollama) -> citation check -> answer + sources
              | redirect          | decline (not enough support)                              | decline (invalid citation)
profile  -> Python rules (guidelines.py) -> short habit notes -> (only these notes go to the model)
```
- The **rules** do all the numbers. The **model** only rewrites retrieved passages in calm language and must tag every claim `[S1]`.
- Personal fields (profile, question, answer) are **encrypted at rest** (Fernet) in SQLite; the model runs **locally**.

## Current status (P4 prototype)

| Requirement | Status | Where |
|---|---|---|
| FR1 Consent gate | Done | `main.py` (`require_consent`), `database.py` |
| FR2 Habit profile, range-checked, view/edit | Done | `schemas.py`, `/api/profile`, `frontend/src/App.jsx` |
| FR3 Guideline rules (sleep by age, activity, strength, sitting, screen) | Done | `backend/app/guidelines.py` |
| FR4 RAG answers with source title, organization, link | Partial (4 starter notes) | `rag.py`, `llm.py`, `pipeline.py`, `scripts/ingest.py` |
| FR5 Safety redirection (9-1-1, Health811 8-1-1, 9-8-8) | Done (keyword-based) | `safety.py` |
| FR6 Decline when unsupported / invalid citation | Done | `rag.py`, `citations.py` |
| FR7 History and 1-5 ratings | Done | `/api/history`, `/api/feedback` |
| FR8 Delete all data | Done | `/api/my-data`, "Delete all my data" button |
| NFR1 Encryption at rest, local LLM | Done | `crypto.py`, `llm.py` |
| Evaluation (Llama vs Gemma, RAG vs no RAG) | Started: first Llama + RAG run on 52 cases: outcome 48/52, redirect 15/15, decline 11/11, rules 8/8, source hit 18/26, median 21.8 s. Gemma and no-RAG runs still to do | `evaluation/` |

## Project structure
```
health-assist/
├── backend/app/        FastAPI app (main.py), safety.py, guidelines.py, rag.py, llm.py, pipeline.py,
│                       citations.py, crypto.py, database.py, schemas.py, config.py
├── frontend/           React (Vite) interface (consent, profile, model choice, chat, sources, history)
├── data/knowledge_base/  approved source notes (TITLE / ORG / URL header + text)
├── scripts/            ingest.py (rebuild index), time_ask.py (response time), show_encrypted.py (privacy check)
├── tests/              pytest tests (rules, safety, citation check, pipeline, API, test-set checks)
├── evaluation/         test_cases.json (52 cases) + run_eval.py (Llama vs Gemma, RAG vs no RAG)
└── docs/               P3 and P4 reports, diagrams, SOURCES.md, screenshots/
```

## How to run
Requirements: Python 3.10-3.12, Node 18+, [Ollama](https://ollama.com).

```bash
# 1. models (one time)
ollama pull llama3.1:8b
ollama pull gemma2:9b          # only needed for the model comparison

# 2. backend (from the project root)
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m scripts.ingest                                 # build the vector index
uvicorn backend.app.main:app --reload                    # http://localhost:8000/docs

# 3. frontend (new terminal)
cd frontend && npm install && npm run dev                # http://localhost:5173
```

## Tests, checks and evaluation
```bash
python -m pytest                      # unit and API tests, no Ollama needed
python -m scripts.show_encrypted      # shows ciphertext in the database (privacy check)
python scripts/time_ask.py            # answer time (backend + Ollama running; run twice, use the 2nd round)
python -m evaluation.run_eval         # all cases, both models, RAG and no RAG (slow)
python -m evaluation.run_eval --models llama3.1:8b --modes rag    # quicker first run
python -m evaluation.summarize        # re-print the summary of the newest results CSV (no re-run)
```
`run_eval` (and `evaluation.summarize`) list every mismatching case and every wrong-source case. `run_eval` saves a CSV in `evaluation/results/` with automatic columns (outcome, source hit, guideline agreement, seconds)
and empty manual columns (faithful, citation_ok, tone_calm) that both team members fill in independently.

## Configuration
Defaults work out of the box. Optional settings (see `.env.example`): `OLLAMA_URL`, `LLM_MODEL`, `MAX_DISTANCE`, `APP_SECRET_KEY`.
Copy `.env.example` to `.env` (not committed). If `APP_SECRET_KEY` is empty a key file is created at `data/secret.key` (git-ignored).
Generate your own key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

## Important notes and limitations
- The files in `data/knowledge_base/` are short paraphrased notes. Check them against the official pages (the URL is in each file header) before final submission; see `docs/SOURCES.md`.
- Hydration has no exact daily number in Canada's Food Guide, so it is answered by retrieval only and is not part of the rule-based comparison.
- The safety filter is keyword-based: it can miss new wordings and sometimes redirects harmless questions (e.g. "symptoms of sleep deprivation"). The test set measures this.
- Encryption protects data at rest, but it is not end-to-end encryption and it is not PIPEDA certification. Timestamps, outcome labels and source lists are not encrypted.
- Chroma's anonymous telemetry is disabled in code, so no outside service is contacted. (If you ever see "Failed to send telemetry event" messages, update `rag.py` to the version in this repo.)
- Prototype limitation: one local user, no login.
- The first run of `python -m scripts.ingest` downloads a small embedding model (about 80 MB) for ChromaDB, so you need internet once.
- Tests use fake model/search responses, so `python -m pytest` runs without Ollama.
