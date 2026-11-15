"""
HealthAssist - One-Click Application Launcher
Course: COMP 4310 - Web Health Informatics (Lakehead University)
Team: Code Health Crew (Nihar Poojari & Dinesh Reddy Morthala)

Usage:
    python run_app.py
"""

import sys
import os
import time
import webbrowser
import urllib.request
from pathlib import Path

# Banner
BANNER = """
========================================================================
   🌿 HealthAssist: Evidence-Grounded Lifestyle Habits Assistant 🌿
         COMP 4310 - Web Health Informatics | Lakehead University
              Team: Code Health Crew (Nihar & Dinesh)
========================================================================
"""

def check_ollama():
    """Checks if the local Ollama daemon is active on port 11434."""
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1.5)
        return True
    except Exception:
        return False

def run_self_tests():
    """Quick sanity test of habit rules and safety triage before starting server."""
    print("[1/3] Running student verification self-tests...")
    try:
        from backend.app.rules.habit_evaluator import evaluate_lifestyle_habits
        from backend.app.triage.safety_guardrail import inspect_query_safety

        # Test habit rules
        res = evaluate_lifestyle_habits(6.0, 90, 10.0, 1.5)
        assert res["sleep"]["status"] == "DEFICIT"
        assert res["sedentary_time"]["status"] == "EXCESSIVE"

        # Test safety triage
        safe_check = inspect_query_safety("I have chest pain and numbness")
        assert safe_check["is_safe"] is False
        assert safe_check["triage_type"] == "EMERGENCY"

        print("      ✓ Deterministic habit evaluation passed.")
        print("      ✓ Safety triage 8-1-1 / 9-1-1 interception passed.")
        return True
    except Exception as e:
        print(f"      ✗ Self-test warning: {e}")
        return False

def main():
    print(BANNER)
    run_self_tests()

    print("[2/3] Checking Local Model Daemon (Ollama)...")
    if check_ollama():
        print("      ✓ Local Ollama daemon detected on http://localhost:11434.")
    else:
        print("      ℹ Ollama daemon not currently detected on port 11434.")
        print("        Running in Grounded Canadian Guidelines Engine (Offline Fallback Mode).")
        print("        (The application will run with full functionality!)")

    print("[3/3] Launching FastAPI backend server on http://127.0.0.1:8000...")
    print("      Open your browser to http://localhost:8000 to interact with HealthAssist.")
    print("      Press Ctrl+C to terminate the local server.\n")

    # Open browser after a brief delay
    time.sleep(1.0)
    try:
        webbrowser.open("http://localhost:8000")
    except Exception:
        pass

    try:
        import uvicorn
        uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, log_level="info")
    except ImportError:
        print("Error: 'uvicorn' or 'fastapi' not installed. Please run: pip install -r backend/requirements.txt")

if __name__ == "__main__":
    main()
