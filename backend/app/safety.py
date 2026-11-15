# safety.py - runs BEFORE retrieval. Catches emergencies, self-harm, diagnosis, medication and treatment requests.
import re

EMERGENCY_MSG = ("This sounds like it could be urgent. Please call 9-1-1 or go to your nearest emergency department right away. "
                 "I'm only a lifestyle information assistant and can't help with emergencies.")
SELF_HARM_MSG = ("I'm really sorry you are going through this. You don't have to handle it alone. In Canada you can call or text 9-8-8 "
                 "(Suicide Crisis Helpline) at any time, or call 9-1-1 if you are in immediate danger.")
MEDICAL_MSG = ("I can only share general wellness information about sleep, activity, nutrition and hydration, so I can't help with "
               "diagnosis, medication or treatment. A doctor, nurse or pharmacist is the right person for this. In Ontario you can call Health811 "
               "(8-1-1) for free advice. If you think it is an emergency, call 9-1-1.")

PATTERNS = [
    ("self_harm", SELF_HARM_MSG, r"suicid|kill myself|end my life|hurt myself|self[- ]harm|want to die|ending it all|end it all|can'?t go on|no reason to live|better off dead|take my own life"),
    ("emergency", EMERGENCY_MSG, r"chest pain|chest (hurts?|is tight|pressure)|coughing (up )?blood|can'?t breathe|cannot breathe|trouble breathing|heart attack|stroke|overdos|severe bleeding|unconscious|passed out|seizure"),
    ("medication", MEDICAL_MSG, r"\bdos(e|age)\b|prescri|medication|medicine|antidepressant|\bmeds?\b|antibiotic|ibuprofen|tylenol|acetaminophen|sleeping pill|melatonin|should i take|\bpills?\b"),
    ("diagnosis", MEDICAL_MSG, r"do i have|diagnos|is (it|this) (cancer|a tumou?r)|\blump\b|what disease|what illness|symptoms? of|am i sick"),
    ("treatment", MEDICAL_MSG, r"how (do i|to) (treat|cure)|treatment for|therapy for|cure for"),
]


def check_safety(question: str):
    """Returns None if the question is okay, otherwise a dict with the category and the calm reply."""
    text = question.lower()
    for category, message, pattern in PATTERNS:
        if re.search(pattern, text):
            return {"category": category, "message": message}
    return None
