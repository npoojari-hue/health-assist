from backend.app.guidelines import compare_habits


def status(results, topic):
    return [r["status"] for r in results if r["topic"] == topic][0]


def test_sleep_below_range():
    assert status(compare_habits({"age": 30, "sleep_hours": 5.5}), "sleep") == "below"


def test_sleep_in_range():
    assert status(compare_habits({"age": 30, "sleep_hours": 8}), "sleep") == "meets"


def test_sleep_older_adult_range_is_7_to_8():
    assert status(compare_habits({"age": 70, "sleep_hours": 8.5}), "sleep") == "above"


def test_activity_boundary_150_meets():
    assert status(compare_habits({"active_minutes_week": 150}), "activity") == "meets"


def test_activity_below():
    assert status(compare_habits({"active_minutes_week": 90}), "activity") == "below"


def test_sitting_above_limit():
    assert status(compare_habits({"sitting_hours_day": 10}), "sitting") == "above"


def test_missing_fields_are_unknown_not_guessed():
    results = compare_habits({})
    assert status(results, "sleep") == "unknown"
    assert status(results, "activity") == "unknown"


def test_wording_has_no_alarm_words():
    for r in compare_habits({"age": 30, "sleep_hours": 3, "active_minutes_week": 0, "sitting_hours_day": 14}):
        assert not any(w in r["message"].lower() for w in ["danger", "serious", "disease", "warning"])
