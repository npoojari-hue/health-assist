# citations.py - checks that every [S1]-style tag in an answer points to a passage that was really retrieved
import re


def check_citations(text: str, passages: list) -> bool:
    """True only if the answer cites at least one passage and every cited tag was really retrieved."""
    cited = set(re.findall(r"\[(S\d+)\]", text))
    valid = {p["sid"] for p in passages}
    return len(cited) > 0 and cited.issubset(valid)
