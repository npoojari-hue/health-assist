# Knowledge-base sources

The notes in `data/knowledge_base/` are **short paraphrased notes** written by the team. Each file starts with TITLE / ORG / URL lines
that the app shows to the user as the source of an answer.

| File | Title | Organization | URL | Used for |
|---|---|---|---|---|
| `physical_activity_csep.txt` | Canadian 24-Hour Movement Guidelines for Adults (18-64 and 65+) | CSEP / PHAC | https://csepguidelines.ca/guidelines/adults-18-64/ | sleep (7-9 h, 7-8 h for 65+), 150 min activity, 2 strength days, 8 h sitting, 3 h screen |
| `sedentary_screen.txt` | Canadian 24-Hour Movement Guidelines - Sedentary behaviour | CSEP / PHAC | https://csepguidelines.ca/guidelines/adults-18-64/ | sitting and recreational screen time, breaking up sitting |
| `physical_activity_who.txt` | WHO Guidelines on Physical Activity and Sedentary Behaviour (adults) | World Health Organization | https://www.who.int/news-room/fact-sheets/detail/physical-activity | 150-300 min moderate or 75-150 min vigorous, strength 2+ days, "some activity is better than none" |
| `hydration_nutrition.txt` | Canada's Food Guide - Healthy eating recommendations | Health Canada | https://food-guide.canada.ca/en/healthy-eating-recommendations/ | water as drink of choice, no exact daily amount, food-group advice |

## Verification log (fill in before final submission)

| File | Checked against official page | Checked by | Date | Terms of use reviewed | Notes |
|---|---|---|---|---|---|
| `physical_activity_csep.txt` | [ ] | | | [ ] | |
| `sedentary_screen.txt` | [ ] | | | [ ] | |
| `physical_activity_who.txt` | [ ] | | | [ ] | |
| `hydration_nutrition.txt` | [ ] | | | [ ] | |

Rules for editing the knowledge base: keep notes short and paraphrased, keep the TITLE / ORG / URL header, then run `python -m scripts.ingest`.
Reference values used by the rules (`backend/app/guidelines.py`) must match these notes.
