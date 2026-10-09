
import re


# Canonical names for common equivalent skill terms.
SKILL_ALIASES = {
    "js": "javascript",
    "ecmascript": "javascript",
    "javascript es6": "javascript",
    "react.js": "react",
    "reactjs": "react",
    "nodejs": "node.js",
    "node js": "node.js",
    "restful api": "rest api",
    "restful apis": "rest api",
    "rest apis": "rest api",
    "restful services": "rest api",
    "structured query language": "sql",
}


def normalize_skill(skill: str) -> str:
    """Normalize a skill name without merging unrelated technologies."""
    if not isinstance(skill, str):
        return ""

    normalized = re.sub(r"\s+", " ", skill.strip().lower())

    if not normalized:
        return ""

    return SKILL_ALIASES.get(normalized, normalized)


def calculate_skill_match(
    resume_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str]
) -> dict:
    """Match normalized skills with explicit compatibility rules."""

    resume_set = {
        normalize_skill(skill)
        for skill in (resume_skills or [])
        if normalize_skill(skill)
    }
    required_set = {
        normalize_skill(skill)
        for skill in (required_skills or [])
        if normalize_skill(skill)
    }
    preferred_set = {
        normalize_skill(skill)
        for skill in (preferred_skills or [])
        if normalize_skill(skill)
    }

    # SQL-family compatibility is an explicit matching policy.
    compatibility = {
        "sql": {"sql", "mysql", "postgresql"},
    }

    def is_covered(required_skill: str) -> bool:
        acceptable = compatibility.get(
            required_skill, {required_skill}
        )
        return bool(resume_set.intersection(acceptable))

    required_matched = sorted(
        skill for skill in required_set if is_covered(skill)
    )
    required_missing = sorted(
        required_set - set(required_matched)
    )

    preferred_matched = sorted(
        skill for skill in preferred_set if is_covered(skill)
    )
    preferred_missing = sorted(
        preferred_set - set(preferred_matched)
    )

    required_coverage = (
        len(required_matched) / len(required_set) * 100
        if required_set else 0.0
    )
    preferred_coverage = (
        len(preferred_matched) / len(preferred_set) * 100
        if preferred_set else 0.0
    )

    if required_set and preferred_set:
        score = required_coverage * 0.80 + preferred_coverage * 0.20
    elif required_set:
        score = required_coverage
    elif preferred_set:
        score = preferred_coverage
    else:
        score = 0.0

    return {
        "score": round(score, 2),
        "coverage": round(required_coverage, 2),
        "required_coverage": round(required_coverage, 2),
        "preferred_coverage": round(preferred_coverage, 2),
        "matched": required_matched,
        "missing": required_missing,
        "preferred_matched": preferred_matched,
        "preferred_missing": preferred_missing,
        "required_skill_count": len(required_set),
        "matched_skill_count": len(required_matched),
        "missing_skill_count": len(required_missing),
        "preferred_skill_count": len(preferred_set),
        "preferred_matched_count": len(preferred_matched),
        "preferred_missing_count": len(preferred_missing),
    }