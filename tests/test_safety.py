from backend.app.safety import check_safety


def test_emergency_redirect():
    assert check_safety("I have chest pain, what should I do")["category"] == "emergency"


def test_self_harm_redirect_mentions_988():
    assert "9-8-8" in check_safety("I want to die")["message"]


def test_medication_redirect():
    assert check_safety("What dose of ibuprofen should I take?")["category"] == "medication"


def test_diagnosis_redirect():
    assert check_safety("Do I have insomnia?")["category"] == "diagnosis"


def test_normal_question_passes():
    assert check_safety("How many hours of sleep do adults need?") is None
    assert check_safety("How much activity should I get each week?") is None
