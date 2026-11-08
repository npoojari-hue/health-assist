# pipeline.py - the full question flow: safety -> retrieval -> generation -> citation check
import re
import requests

from .guidelines import compare_habits, summary_text
from .citations import check_citations
from .llm import ask_model
from .rag import retrieve
from .safety import check_safety

DISCLAIMER = "This is general wellness information, not medical advice."

SYSTEM_PROMPT = """You are HealthAssist, a calm and kind assistant that shares general wellness information for adults in Canada.
Rules:
1. Use ONLY the numbered passages given to you. If they do not answer the question, say you cannot answer.
2. After every statement that comes from a passage, add its tag, for example [S1].
3. Never diagnose, never mention medication or treatment, never use scary or pressuring words.
4. Suggestions must be gentle and optional ("you could try", "if you like").
5. Do not do your own maths. Use the habit notes exactly as they are written.
6. Keep the answer short (under 150 words) and use simple language."""

DECLINE_MSG = ("I'm sorry, my approved Canadian and WHO sources don't cover that well enough for me to answer reliably. "
               "You could try the official Health Canada or WHO websites, or ask a healthcare professional.")


def answer_question(question: str, profile: dict = None, model: str = None, use_rag: bool = True) -> dict:
    # 1. safety check first
    flagged = check_safety(question)
    if flagged:
        return {"outcome": "redirected", "category": flagged["category"], "answer": flagged["message"],
                "sources": [], "comparison": [], "passages": []}

    comparison = compare_habits(profile) if profile else []

    # 2. retrieval (skipped only for the no-RAG baseline in the evaluation)
    passages = retrieve(question) if use_rag else []
    if use_rag and not passages:
        return {"outcome": "declined", "answer": DECLINE_MSG, "sources": [], "comparison": comparison, "passages": []}

    # 3. generation. Only the rule results are sent to the model, not the raw profile (data minimization).
    context = "\n\n".join(f"[{p['sid']}] ({p['org']}) {p['text']}" for p in passages)
    user_prompt = f"Question: {question}\n\nHabit notes about the user:\n{summary_text(comparison)}\n\nPassages:\n{context or '(none)'}"
    try:
        text = ask_model(SYSTEM_PROMPT, user_prompt, model)
    except requests.RequestException:
        return {"outcome": "error", "answer": "The local AI model is not running. Please start Ollama and try again.",
                "sources": [], "comparison": comparison, "passages": passages}

    # 4. citation check before showing anything
    if use_rag and not check_citations(text, passages):
        return {"outcome": "declined_uncited", "answer": DECLINE_MSG, "sources": [],
                "comparison": comparison, "passages": passages}

    cited = set(re.findall(r"\[(S\d+)\]", text))
    sources, seen = [], set()
    for p in passages:
        if p["sid"] in cited and p["url"] not in seen:
            seen.add(p["url"])
            sources.append({"title": p["title"], "org": p["org"], "url": p["url"], "doc_id": p["doc_id"]})
    clean = re.sub(r"\s*\[S\d+\]", "", text)
    return {"outcome": "answered", "answer": f"{clean}\n\n{DISCLAIMER}", "sources": sources,
            "comparison": comparison, "passages": passages}
