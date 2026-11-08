# run_eval.py - runs every test case through the pipeline for each model, with and without RAG.
# usage (project root, Ollama running):  python -m evaluation.run_eval
# Automatic columns: outcome_ok, source_hit.  Manual columns (we fill these in by hand): faithful, citation_ok, tone_calm.
import csv
import json
from datetime import datetime
from pathlib import Path

from backend.app.pipeline import answer_question

HERE = Path(__file__).parent
MODELS = ["llama3.1:8b", "gemma2:9b"]
MODES = [("rag", True), ("no_rag", False)]


def main():
    cases = json.loads((HERE / "test_cases.json").read_text(encoding="utf-8"))
    out_file = HERE / "results" / f"results_{datetime.now():%Y%m%d_%H%M}.csv"
    rows = []
    for model in MODELS:
        for mode_name, use_rag in MODES:
            for case in cases:
                res = answer_question(case["question"], case.get("profile"), model=model, use_rag=use_rag)
                outcome = "answered" if res["outcome"] == "answered" else res["outcome"].replace("_uncited", "")
                sources = [s["doc_id"] for s in res["sources"]]
                rows.append({
                    "case_id": case["id"], "type": case["type"], "model": model, "mode": mode_name,
                    "expected_outcome": case["expected_outcome"], "actual_outcome": outcome,
                    "outcome_ok": outcome == case["expected_outcome"],
                    "source_hit": (case.get("expected_source") in sources) if case.get("expected_source") else "",
                    "answer": res["answer"].replace("\n", " "),
                    "faithful": "", "citation_ok": "", "tone_calm": "",
                })
                print(case["id"], model, mode_name, outcome)
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("saved", out_file)
    for model in MODELS:
        for mode_name, _ in MODES:
            subset = [r for r in rows if r["model"] == model and r["mode"] == mode_name]
            ok = sum(r["outcome_ok"] for r in subset)
            print(f"{model} {mode_name}: outcome accuracy {ok}/{len(subset)}")


if __name__ == "__main__":
    main()
