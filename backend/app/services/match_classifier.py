def classify_match(
    match_score: float,
    skill_coverage: float,
    content_alignment: float
) -> dict:

    # ---------------------------------------------
    # STRONG MATCH
    # ---------------------------------------------
    if (
        match_score >= 70
        and skill_coverage >= 90
        and content_alignment >= 70
    ):
        label = "strong_match"

    # ---------------------------------------------
    # WEAK MATCH
    # ---------------------------------------------
    elif match_score < 40:
        label = "weak_match"

    # ---------------------------------------------
    # MODERATE MATCH
    # ---------------------------------------------
    else:
        label = "moderate_match"

    return {
        "label": label,
        "confidence": calculate_classification_confidence(
            match_score,
            skill_coverage,
            content_alignment,
            label
        )
    }


def calculate_classification_confidence(
    match_score: float,
    skill_coverage: float,
    content_alignment: float,
    label: str
) -> float:

    if label == "strong_match":

        score_confidence = min(
            max((match_score - 70) / 30, 0),
            1
        )

        skill_confidence = min(
            max((skill_coverage - 90) / 10, 0),
            1
        )

        content_confidence = min(
            max((content_alignment - 70) / 30, 0),
            1
        )

        confidence = (
            score_confidence * 0.40
            + skill_confidence * 0.30
            + content_confidence * 0.30
        )

    elif label == "moderate_match":

        distance_from_strong = min(
            abs(match_score - 70) / 30,
            1
        )

        confidence = (
            0.5
            + distance_from_strong * 0.5
        )

    else:

        confidence = min(
            (40 - match_score) / 40,
            1
        )

    return round(
        confidence * 100,
        2
    )