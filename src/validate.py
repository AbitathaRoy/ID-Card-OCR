# src/validate.py

from difflib import SequenceMatcher

def name_similarity(name1: str | None, name2: str | None) -> float:
    if not name1 or not name2:
        return 0.0

    name1 = name1.lower().strip()
    name2 = name2.lower().strip()

    return SequenceMatcher(None, name1, name2).ratio()

def exact_match(a, b) -> float:
    if a is None or b is None:
        return 0.0
    return 1.0 if str(a) == str(b) else 0.0

def validate_record(row: dict) -> dict:
    """
    Takes a DB row (as dict) and returns validation scores.
    """

    scores = {
        "name_score": name_similarity(
            row["typed_name"], row["ocr_name"]
        ),
        "phone_score": exact_match(
            row["typed_phone"], row["ocr_phone"]
        ),
        "year_score": exact_match(
            row["typed_year_of_study"], row["computed_year_of_study"]
        )
    }

    # weighted overall confidence
    scores["overall_confidence"] = (
        0.4 * scores["name_score"] +
        0.3 * scores["phone_score"] +
        0.3 * scores["year_score"]
    )

    return scores