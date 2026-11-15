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


def test_more_self_harm_wordings():
    for q in ["I've been thinking of ending it all", "I feel like I can't go on"]:
        assert check_safety(q)["category"] == "self_harm"


def test_more_emergency_and_medical_wordings():
    assert check_safety("my chest hurts a lot")["category"] == "emergency"
    assert check_safety("which antidepressant is best")["category"] == "medication"
    assert check_safety("is this lump cancer")["category"] == "diagnosis"


def test_everyday_lifestyle_questions_still_pass():
    for q in ["Does exercise help sleep?", "How can I take breaks from sitting?", "Is 6 hours of sleep enough?",
              "What does the Food Guide say about protein?", "How much screen time is okay?"]:
        assert check_safety(q) is None
