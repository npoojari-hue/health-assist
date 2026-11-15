# run_eval.py - runs every test case through the pipeline for each model, with and without RAG.
# usage (project root, Ollama running):  python -m evaluation.run_eval
# Optional:  python -m evaluation.run_eval --models llama3.1:8b --modes rag     (faster first run)
# Automatic columns: outcome_ok, source_hit, guideline_ok.
# Manual columns (we fill these in by hand, 1 = yes / 0 = no, tone 1-5): faithful, citation_ok, tone_calm.
import argparse
import csv
import json
import statistics
import time
from datetime import datetime
from pathlib import Path

from backend.app.pipeline import answer_question

HERE = Path(__file__).parent
ALL_MODELS = ["llama3.1:8b", "gemma2:9b"]
ALL_MODES = {"rag": True, "no_rag": False}


def expected_guidelines(case):
    g = case.get("expected_guideline")
    return [g] if isinstance(g, str) else (g or [])


def guideline_ok(case, comparison):
    """True if every expected 'topic status' pair (e.g. 'sleep below') appears in the rule results. '' if not applicable."""
    expected = expected_guidelines(case)
    if not expected:
        return ""
    shown = {f"{r['topic']} {r['status']}" for r in comparison}
    return all(e in shown for e in expected)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=ALL_MODELS)
    parser.add_argument("--modes", nargs="+", default=list(ALL_MODES), choices=list(ALL_MODES))
    args = parser.parse_args()

    cases = json.loads((HERE / "test_cases.json").read_text(encoding="utf-8"))
    out_file = HERE / "results" / f"results_{datetime.now():%Y%m%d_%H%M}.csv"
    out_file.parent.mkdir(exist_ok=True)
    rows = []
    for model in args.models:
        for mode_name in args.modes:
            for case in cases:
                start = time.time()
                res = answer_question(case["question"], case.get("profile"), model=model, use_rag=ALL_MODES[mode_name])
                seconds = round(time.time() - start, 1)
                outcome = "answered" if res["outcome"] == "answered" else res["outcome"].replace("_uncited", "")
                sources = [s["doc_id"] for s in res["sources"]]
                rows.append({
                    "case_id": case["id"], "type": case["type"], "model": model, "mode": mode_name,
                    "expected_outcome": case["expected_outcome"], "actual_outcome": outcome,
                    "raw_outcome": res["outcome"],
                    "outcome_ok": outcome == case["expected_outcome"],
                    "source_hit": (case.get("expected_source") in sources) if case.get("expected_source") else "",
                    "guideline_ok": guideline_ok(case, res.get("comparison", [])),
                    "seconds": seconds,
                    "sources": ";".join(sources),
                    "answer": res["answer"].replace("\n", " "),
                    "faithful": "", "citation_ok": "", "tone_calm": "",
                })
                print(case["id"], model, mode_name, outcome, f"{seconds}s")
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("saved", out_file)

    print_summary(rows, args.models, args.modes)


def print_summary(rows, models, modes):
    """One short line per measure so the whole summary fits on screen (good for the screenshot)."""
    print("\n=== summary ===")
    for model in models:
        for mode_name in modes:
            subset = [r for r in rows if r["model"] == model and r["mode"] == mode_name]
            if not subset:
                continue
            ok = sum(str(r["outcome_ok"]) == "True" for r in subset)
            print(f"\n{model} | {mode_name}")
            print(f"  outcome accuracy : {ok}/{len(subset)}")
            for t in ("in_scope", "profile", "out_of_scope", "unanswerable"):
                part = [r for r in subset if r["type"] == t]
                if part:
                    print(f"    {t:<13}: {sum(str(r['outcome_ok']) == 'True' for r in part)}/{len(part)}")
            hits = [r for r in subset if str(r["source_hit"]) != ""]
            if hits:
                print(f"  source hit       : {sum(str(r['source_hit']) == 'True' for r in hits)}/{len(hits)}")
            gl = [r for r in subset if str(r["guideline_ok"]) != ""]
            if gl:
                print(f"  guideline agree  : {sum(str(r['guideline_ok']) == 'True' for r in gl)}/{len(gl)}")
            answered = [float(r["seconds"]) for r in subset if r["actual_outcome"] == "answered"]
            if answered:
                print(f"  median answer    : {statistics.median(answered)} s (over {len(answered)} answered)")
            questions = {c["id"]: c for c in json.loads((HERE / "test_cases.json").read_text(encoding="utf-8"))}
            for r in subset:
                if str(r["outcome_ok"]) != "True":
                    q = questions.get(r["case_id"], {}).get("question", "")
                    print(f"  MISMATCH {r['case_id']}: expected {r['expected_outcome']}, got {r['raw_outcome']} | {q}")
            for r in hits:
                if str(r["source_hit"]) != "True" and r["actual_outcome"] == "answered":
                    c = questions.get(r["case_id"], {})
                    print(f"  WRONG SOURCE {r['case_id']}: expected {c.get('expected_source')}, cited {r.get('sources', '(not saved in this CSV)')} | {c.get('question', '')}")

if __name__ == "__main__":
    main()
