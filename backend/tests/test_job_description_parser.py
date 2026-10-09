from app.services.job_description_parser import extract_experience_requirement
from app.services.job_description_parser import extract_jd_skills


def test_required_skills_are_classified_as_required():
    jd = """
    Requirements
    - Strong knowledge of Python.
    - Strong knowledge of JavaScript.
    - Experience with React.js.
    """

    result = extract_jd_skills(jd)

    assert {"python", "javascript", "react"}.issubset(
        set(result["required"])
    )


def test_skills_only_in_preferred_section_are_preferred():
    jd = """
    Requirements
    - Strong knowledge of Python.

    Preferred Skills
    - AWS
    - MongoDB
    """

    result = extract_jd_skills(jd)

    assert "python" in result["required"]
    assert "aws" in result["preferred"]
    assert "mongodb" in result["preferred"]


def test_required_skill_is_not_duplicated_as_preferred():
    jd = """
    Requirements
    - Strong knowledge of JavaScript.

    Preferred Skills
    - JavaScript
    - AWS
    """

    result = extract_jd_skills(jd)

    assert "javascript" in result["required"]
    assert "javascript" not in result["preferred"]
    assert "aws" in result["preferred"]

    from app.services.job_description_parser import (
    extract_experience_requirement,
)


def test_extract_plus_years_requirement():
    text = "Experience: 2+ years of professional backend development."
    assert extract_experience_requirement(text) == "2+ years"


def test_extract_year_range_requirement():
    text = "Experience: 0-1 years."
    assert extract_experience_requirement(text) == "0-1 years"


def test_missing_experience_requirement():
    text = "Software Engineer. Requirements: Python and SQL."
    assert extract_experience_requirement(text) is None