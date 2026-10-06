import re

from app.services.skill_extractor import extract_skills


# --------------------------------------------------
# SECTION ALIASES
# --------------------------------------------------

SECTION_ALIASES = {
    "requirements": [
        "requirements",
        "required qualifications",
        "required skills",
        "qualifications",
        "what we're looking for",
        "what we are looking for"
    ],

    "preferred": [
        "preferred qualifications",
        "preferred skills",
        "nice to have",
        "nice-to-have",
        "preferred"
    ],

    "responsibilities": [
        "responsibilities",
        "job responsibilities",
        "roles and responsibilities",
        "what you'll do",
        "what you will do",
        "duties"
    ],

    "education": [
        "education",
        "educational requirements",
        "academic requirements"
    ],

    "experience": [
        "experience",
        "experience required",
        "work experience"
    ]
}


def clean_line(text: str) -> str:

    return re.sub(
        r"\s+",
        " ",
        text.strip()
    )


def normalize_heading(text: str) -> str:

    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9\s&'-]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text


def detect_section_heading(line: str):

    normalized = normalize_heading(line)

    for section, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            if normalized == normalize_heading(alias):
                return section

    return None


# --------------------------------------------------
# JOB TITLE
# --------------------------------------------------

def extract_job_title(text: str) -> str | None:

    lines = [
        clean_line(line)
        for line in text.splitlines()
        if clean_line(line)
    ]

    title_keywords = [
        "developer",
        "engineer",
        "designer",
        "analyst",
        "manager",
        "consultant",
        "scientist",
        "intern"
    ]

    for line in lines[:10]:

        line_lower = line.lower()

        if any(
            keyword in line_lower
            for keyword in title_keywords
        ):
            return line

    return None


# --------------------------------------------------
# EXPERIENCE REQUIREMENT
# --------------------------------------------------

def extract_experience_requirement(text: str) -> str | None:
    patterns = [
        r"\b\d+\s*-\s*\d+\s*(?:years?|yrs?)\b",
        r"\b\d+\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience\b",
        r"\bminimum\s+of\s+\d+\s*(?:years?|yrs?)\b",
        r"\bat\s+least\s+\d+\s*(?:years?|yrs?)\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(0)

    return None


# --------------------------------------------------
# EDUCATION REQUIREMENTS
# --------------------------------------------------

def extract_education_requirements(text: str) -> list[str]:
    education_keywords = [
        "bachelor", "b.tech", "b.e", "bca", "b.sc",
        "master", "m.tech", "m.e", "mca", "m.sc", "mba",
        "phd", "degree"
    ]

    education_lines = []

    for line in text.splitlines():
        cleaned = clean_line(line)

        if not cleaned:
            continue

        line_lower = cleaned.lower()

        if any(keyword in line_lower for keyword in education_keywords):
            education_lines.append(cleaned)

    return sorted(set(education_lines))


# --------------------------------------------------
# RESPONSIBILITIES
# --------------------------------------------------

def extract_responsibilities(
    text: str
) -> list[str]:

    responsibilities = []

    current_section = None

    for line in text.splitlines():

        cleaned = clean_line(line)

        if not cleaned:
            continue

        section = detect_section_heading(cleaned)

        if section:

            current_section = section
            continue

        if current_section == "responsibilities":

            cleaned = re.sub(
                r"^[•●▪◦*-]\s*",
                "",
                cleaned
            )

            if cleaned:
                responsibilities.append(
                    cleaned
                )

    return responsibilities


# --------------------------------------------------
# REQUIRED / PREFERRED SKILLS
# --------------------------------------------------

def extract_jd_skills(text: str) -> dict:

    all_skills = extract_skills(text)

    preferred_section = []

    current_section = None

    for line in text.splitlines():

        cleaned = clean_line(line)

        if not cleaned:
            continue

        section = detect_section_heading(cleaned)

        if section:

            current_section = section
            continue

        if current_section == "preferred":

            preferred_section.append(cleaned)

    preferred_text = "\n".join(
        preferred_section
    )

    preferred_skills = extract_skills(
        preferred_text
    )

    preferred_set = set(preferred_skills)

    required_skills = [
        skill
        for skill in all_skills
        if skill not in preferred_set
    ]

    return {
        "required": sorted(required_skills),
        "preferred": sorted(preferred_skills)
    }


# --------------------------------------------------
# MAIN JD PARSER
# --------------------------------------------------

def parse_job_description(
    text: str
) -> dict:

    skills = extract_jd_skills(text)

    return {
        "job_title": extract_job_title(text),

        "required_skills": skills[
            "required"
        ],

        "preferred_skills": skills[
            "preferred"
        ],

        "experience_required":
            extract_experience_requirement(text),

        "education_requirements":
            extract_education_requirements(text),

        "responsibilities":
            extract_responsibilities(text)
    }