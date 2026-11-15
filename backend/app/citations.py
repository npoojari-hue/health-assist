# citations.py - checks that every [S1]-style tag in an answer points to a passage that was really retrieved
import re

# matches [S1] and also grouped tags such as [S1, S2]
TAG_GROUP = re.compile(r"\[\s*(S\d+(?:\s*[,;]\s*S\d+)*)\s*\]")


def extract_tags(text: str) -> set:
    tags = set()
    for group in TAG_GROUP.findall(text):
        tags.update(re.findall(r"S\d+", group))
    return tags


def strip_tags(text: str) -> str:
    return re.sub(r"\s*" + TAG_GROUP.pattern, "", text)


def check_citations(text: str, passages: list) -> bool:
    """True only if the answer cites at least one passage and every cited tag was really retrieved."""
    cited = extract_tags(text)
    valid = {p["sid"] for p in passages}
    return len(cited) > 0 and cited.issubset(valid)
