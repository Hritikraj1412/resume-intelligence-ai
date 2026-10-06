def calculate_skill_match(
    resume_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str]
) -> dict:

    resume_set = {
        skill.lower()
        for skill in resume_skills
    }

    required_set = {
        skill.lower()
        for skill in required_skills
    }

    preferred_set = {
        skill.lower()
        for skill in preferred_skills
    }

    required_matched = sorted(
        resume_set.intersection(required_set)
    )

    required_missing = sorted(
        required_set - resume_set
    )

    preferred_matched = sorted(
        resume_set.intersection(preferred_set)
    )

    preferred_missing = sorted(
        preferred_set - resume_set
    )

    # Required skill coverage
    if required_set:
        required_coverage = (
            len(required_matched)
            / len(required_set)
        ) * 100
    else:
        required_coverage = 0.0

    # Preferred skill coverage
    if preferred_set:
        preferred_coverage = (
            len(preferred_matched)
            / len(preferred_set)
        ) * 100
    else:
        preferred_coverage = 0.0

    # Required skills have higher importance
    if required_set and preferred_set:

        score = (
            required_coverage * 0.80
            + preferred_coverage * 0.20
        )

    elif required_set:

        score = required_coverage

    elif preferred_set:

        score = preferred_coverage

    else:

        score = 0.0

    return {
        "score": round(score, 2),

        "coverage": round(
            required_coverage,
            2
        ),

        "required_coverage": round(
            required_coverage,
            2
        ),

        "preferred_coverage": round(
            preferred_coverage,
            2
        ),

        "matched": required_matched,

        "missing": required_missing,

        "preferred_matched": preferred_matched,

        "preferred_missing": preferred_missing,

        "required_skill_count": len(
            required_set
        ),

        "matched_skill_count": len(
            required_matched
        ),

        "missing_skill_count": len(
            required_missing
        ),

        "preferred_skill_count": len(
            preferred_set
        ),

        "preferred_matched_count": len(
            preferred_matched
        ),

        "preferred_missing_count": len(
            preferred_missing
        )
    }