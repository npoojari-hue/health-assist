# time_ask.py - measures answer time for NFR4. Backend (uvicorn) and Ollama must be running.
# usage (project root):  python scripts/time_ask.py
# Run it twice: round 1 includes loading the model into memory (slow). Report the median of round 2.
# Do not click "Delete all my data" in the browser while it runs (that removes consent and stops the test).
import statistics
import time

import requests

B = "http://localhost:8000/api"
QUESTIONS = [
    "How many hours of sleep do adults need?",
    "How much physical activity should adults get each week?",
    "How long should I sit each day at most?",
    "What does Canada's Food Guide say about water?",
    "How much screen time is okay?",
]


def ensure_consent():
    if not requests.get(f"{B}/consent").json().get("accepted"):
        requests.post(f"{B}/consent")


for round_no in (1, 2):
    times = []
    for q in QUESTIONS:
        ensure_consent()
        t = time.time()
        r = requests.post(f"{B}/ask", json={"text": q}, timeout=600).json()
        dt = time.time() - t
        if "outcome" not in r:
            print(f"round {round_no}: server replied with an error: {r}")
            continue
        if r["outcome"] == "answered":
            times.append(dt)
        print(f"round {round_no}: {dt:5.1f}s  {r['outcome']:<16} {q}")
    if times:
        print(f"round {round_no} median (answered only): {statistics.median(times):.1f}s\n")
