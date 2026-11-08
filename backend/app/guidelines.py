# guidelines.py - habit comparison done with plain Python rules (NOT by the language model).
# Reference values come from the Canadian 24-Hour Movement Guidelines for adults (CSEP).
# Wording is kept calm and optional on purpose.

SLEEP_RANGE_ADULT = (7, 9)    # 18-64 years
SLEEP_RANGE_OLDER = (7, 8)    # 65+ years
ACTIVE_MIN_PER_WEEK = 150     # moderate to vigorous activity
STRENGTH_DAYS = 2
MAX_SITTING_HOURS = 8
MAX_SCREEN_HOURS = 3          # recreational screen time


def _row(topic, status, message, source):
    return {"topic": topic, "status": status, "message": message, "source": source}


def compare_habits(profile: dict) -> list:
    results = []
    age = profile.get("age")
    low, high = SLEEP_RANGE_OLDER if (age is not None and age >= 65) else SLEEP_RANGE_ADULT

    sleep = profile.get("sleep_hours")
    if sleep is None:
        results.append(_row("sleep", "unknown", "No sleep information was shared.", "physical_activity_csep"))
    elif sleep < low:
        results.append(_row("sleep", "below",
            f"You shared about {sleep} hours of sleep. The guideline range for your age group is {low}-{high} hours, "
            "so there may be a little room to gain more rest if you would like to.", "physical_activity_csep"))
    elif sleep > high:
        results.append(_row("sleep", "above",
            f"You shared about {sleep} hours of sleep, a bit above the {low}-{high} hour range. "
            "Needs differ between people, so this is just for your information.", "physical_activity_csep"))
    else:
        results.append(_row("sleep", "meets",
            f"Your sleep ({sleep} hours) is within the {low}-{high} hour range. Nice.", "physical_activity_csep"))

    active = profile.get("active_minutes_week")
    if active is None:
        results.append(_row("activity", "unknown", "No activity information was shared.", "physical_activity_who"))
    elif active >= ACTIVE_MIN_PER_WEEK:
        results.append(_row("activity", "meets",
            f"{active} active minutes a week reaches the {ACTIVE_MIN_PER_WEEK} minute guideline.", "physical_activity_who"))
    else:
        results.append(_row("activity", "below",
            f"You shared {active} active minutes a week. The guideline is at least {ACTIVE_MIN_PER_WEEK}. "
            "Some activity is already better than none, and small steps are fine.", "physical_activity_who"))

    strength = profile.get("strength_days_week")
    if strength is not None:
        if strength >= STRENGTH_DAYS:
            results.append(_row("strength", "meets",
                f"{strength} muscle-strengthening days a week meets the guideline of {STRENGTH_DAYS}.", "physical_activity_csep"))
        else:
            results.append(_row("strength", "below",
                f"The guideline suggests muscle-strengthening on at least {STRENGTH_DAYS} days a week; "
                f"you shared {strength}. This is optional to try.", "physical_activity_csep"))

    sitting = profile.get("sitting_hours_day")
    if sitting is not None:
        if sitting <= MAX_SITTING_HOURS:
            results.append(_row("sitting", "meets",
                f"Sitting {sitting} hours a day is within the {MAX_SITTING_HOURS} hour limit.", "sedentary_screen"))
        else:
            results.append(_row("sitting", "above",
                f"You shared {sitting} hours of sitting a day. The guideline suggests {MAX_SITTING_HOURS} or fewer, "
                "and short breaks to stand or move can help.", "sedentary_screen"))

    screen = profile.get("screen_hours_day")
    if screen is not None:
        if screen <= MAX_SCREEN_HOURS:
            results.append(_row("screen", "meets",
                f"{screen} hours of recreational screen time is within the {MAX_SCREEN_HOURS} hour suggestion.", "sedentary_screen"))
        else:
            results.append(_row("screen", "above",
                f"You shared {screen} hours of recreational screen time. The guideline suggests {MAX_SCREEN_HOURS} or less.",
                "sedentary_screen"))

    # Hydration has no exact number in the Canadian guidance, so it is only handled by retrieval.
    return results


def summary_text(results: list) -> str:
    """Short text version of the results that is given to the language model."""
    if not results:
        return "The user has not shared any habit information."
    return "\n".join(f"- {r['topic']}: {r['message']}" for r in results)
