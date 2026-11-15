# Checks the evaluation test set itself, so the labels cannot silently be wrong. Runs without Ollama.
import json
from pathlib import Path

from backend.app.guidelines import compare_habits
from backend.app.safety import check_safety
from evaluation.run_eval import expected_guidelines, guideline_ok

CASES = json.loads((Path(__file__).parent.parent / "evaluation" / "test_cases.json").read_text(encoding="utf-8"))
KB_IDS = {p.stem for p in (Path(__file__).parent.parent / "data" / "knowledge_base").glob("*.txt")}


def test_case_file_is_well_formed():
    ids = [c["id"] for c in CASES]
    assert len(ids) == len(set(ids))
    assert {c["type"] for c in CASES} == {"in_scope", "profile", "out_of_scope", "unanswerable"}
    for c in CASES:
        assert c["expected_outcome"] in {"answered", "redirected", "declined"}
        if c.get("expected_source"):
            assert c["expected_source"] in KB_IDS


def test_out_of_scope_cases_are_redirected_by_the_safety_filter():
    for c in CASES:
        if c["expected_outcome"] == "redirected":
            assert check_safety(c["question"]), c["id"]


def test_other_cases_are_not_blocked_by_the_safety_filter():
    for c in CASES:
        if c["expected_outcome"] != "redirected":
            assert check_safety(c["question"]) is None, c["id"]


def test_profile_cases_match_the_rule_results():
    checked = 0
    for c in CASES:
        if expected_guidelines(c):
            assert guideline_ok(c, compare_habits(c.get("profile") or {})) is True, c["id"]
            checked += 1
    assert checked >= 8
