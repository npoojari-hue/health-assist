# Pipeline-level tests with a fake model and fake search (no Ollama, no ChromaDB index needed).
import requests

from backend.app import pipeline

PASSAGES = [{"sid": "S1", "text": "Adults need 7 to 9 hours of sleep.", "org": "CSEP", "title": "24h",
             "url": "https://csepguidelines.ca", "doc_id": "physical_activity_csep"}]


def fake(monkeypatch, passages=PASSAGES, reply="Adults need 7 to 9 hours [S1]."):
    seen = {}

    def model(system, user, model_name=None):
        seen["prompt"] = user
        return reply

    monkeypatch.setattr(pipeline, "retrieve", lambda q: passages)
    monkeypatch.setattr(pipeline, "ask_model", model)
    return seen


def test_answer_has_sources_disclaimer_and_no_tags(monkeypatch):
    fake(monkeypatch)
    r = pipeline.answer_question("How much sleep?")
    assert r["outcome"] == "answered" and r["sources"][0]["doc_id"] == "physical_activity_csep"
    assert "[S1]" not in r["answer"] and pipeline.DISCLAIMER in r["answer"]


def test_grouped_tags_are_cleaned_from_the_answer(monkeypatch):
    fake(monkeypatch, reply="Adults need 7 to 9 hours [S1, S1].")
    assert "[S1" not in pipeline.answer_question("How much sleep?")["answer"]


def test_model_gets_habit_notes_not_the_raw_profile(monkeypatch):
    seen = fake(monkeypatch)
    pipeline.answer_question("Am I sleeping enough?", {"age": 41, "sleep_hours": 6.25})
    assert "6.25" in seen["prompt"] and "sleep_hours" not in seen["prompt"]


def test_uncited_answer_is_declined(monkeypatch):
    fake(monkeypatch, reply="Adults need 7 to 9 hours.")
    assert pipeline.answer_question("How much sleep?")["outcome"] == "declined_uncited"


def test_redirect_never_calls_the_model(monkeypatch):
    seen = fake(monkeypatch)
    assert pipeline.answer_question("What dose of ibuprofen should I take?")["outcome"] == "redirected"
    assert "prompt" not in seen


def test_empty_profile_still_gives_rule_rows(monkeypatch):
    fake(monkeypatch)
    rows = pipeline.answer_question("How much sleep?", {})["comparison"]
    assert {r["topic"]: r["status"] for r in rows} == {"sleep": "unknown", "activity": "unknown"}


def test_model_offline_gives_a_friendly_error(monkeypatch):
    fake(monkeypatch)

    def boom(*a, **k):
        raise requests.ConnectionError()

    monkeypatch.setattr(pipeline, "ask_model", boom)
    r = pipeline.answer_question("How much sleep?")
    assert r["outcome"] == "error" and "Ollama" in r["answer"]
