# llm.py - talks to the local Ollama server so nothing is sent to an outside AI service
import requests
from .config import OLLAMA_URL, DEFAULT_MODEL


def ask_model(system: str, user: str, model: str = None) -> str:
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": model or DEFAULT_MODEL,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "stream": False,
            "options": {"temperature": 0.2},
        },
        timeout=300,
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip()
