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
    text = clean_line(text)

    # Support job descriptions written on a single line.
    first_part = re.split(
        r"\b(?:requirements|required qualifications|required skills|"
        r"qualifications|preferred qualifications|preferred skills|"
        r"nice to have|nice-to-have|responsibilities|job responsibilities|"
        r"roles and responsibilities|what you'll do|what you will do|duties)\s*:",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip(" .:-")

    if not first_part:
        return None

    title_keywords = [
        "developer", "engineer", "designer", "analyst",
        "manager", "consultant", "scientist", "intern",
    ]

    if any(keyword in first_part.lower() for keyword in title_keywords):
        return first_part

    return None




# --------------------------------------------------
# EXPERIENCE REQUIREMENT
# --------------------------------------------------

def extract_experience_requirement(text: str) -> str | None:
    patterns = [
        # Examples: 2-4 years, 0-1 yrs
        r"\b\d+\s*-\s*\d+\s*(?:years?|yrs?)\b",

        # Examples: 2+ years, 3+ yrs
        r"\b\d+\s*\+\s*(?:years?|yrs?)\b",

        # Examples: minimum of 2 years, at least 3 yrs
        r"\bminimum\s+of\s+\d+\s*(?:years?|yrs?)\b",
        r"\bat\s+least\s+\d+\s*(?:years?|yrs?)\b",

        # Examples: 2 years of experience, 3 yrs experience
        r"\b\d+\s*(?:years?|yrs?)\s*(?:of\s+)?experience\b",
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

def extract_responsibilities(text: str) -> list[str]:
    aliases = sorted(
        SECTION_ALIASES["responsibilities"],
        key=len,
        reverse=True,
    )

    pattern = re.compile(
        r"(?<!\w)("
        + "|".join(re.escape(alias) for alias in aliases)
        + r")\s*:",
        re.IGNORECASE,
    )

    matches = list(pattern.finditer(text))
    responsibilities = []

    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)

        content = text[start:end].strip()

        if content:
            for item in re.split(r"[\n•●▪◦]+", content):
                item = re.sub(r"^\s*[-*]\s*", "", item).strip(" .;:-")
                if item:
                    responsibilities.append(item)

    return responsibilities



# --------------------------------------------------
# REQUIRED / PREFERRED SKILLS
# --------------------------------------------------

def extract_jd_skills(text: str) -> dict:
    sections = {
        "requirements": [],
        "preferred": [],
    }

    aliases = sorted(
        [
            (alias, section)
            for section, names in SECTION_ALIASES.items()
            if section in sections
            for alias in names
        ],
        key=lambda item: len(item[0]),
        reverse=True,
    )

    alias_pattern = "|".join(
        re.escape(alias) for alias, _ in aliases
    )

    # Supports headings with or without a colon,
    # including headings embedded in a sentence.
    pattern = re.compile(
        r"(?<!\w)(" + alias_pattern + r")\s*:?",
        re.IGNORECASE,
    )

    matches = []

    for line_match in re.finditer(r"[^\n]+", text):
        line = line_match.group()
        stripped = line.strip()

        # Standalone headings, including Markdown/list punctuation.
        normalized = normalize_heading(
            re.sub(r"^[\s\-*•●▪◦]+", "", stripped).rstrip(":")
        )

        standalone_section = next(
            (
                section
                for alias, section in aliases
                if normalized == normalize_heading(alias)
            ),
            None,
        )

        if standalone_section:
            matches.append(
                (line_match.start(), line_match.end(), standalone_section)
            )
            continue

        # Inline headings such as "Requirements: Python..."
        for match in pattern.finditer(line):
            heading = match.group(1).lower()
            section = next(
                section
                for alias, section in aliases
                if alias.lower() == heading
            )
            matches.append(
                (
                    line_match.start() + match.start(),
                    line_match.start() + match.end(),
                    section,
                )
            )

    matches.sort(key=lambda item: item[0])

    for index, (heading_start, content_start, section) in enumerate(matches):
        end = (
            matches[index + 1][0]
            if index + 1 < len(matches)
            else len(text)
        )

        content = text[content_start:end].strip()

        # Remove leading punctuation from section content.
        content = re.sub(r"^[\s:.-]+", "", content)

        if content and section in sections:
            sections[section].append(content)

    required_skills = set(
        extract_skills("\n".join(sections["requirements"]))
    )
    preferred_skills = set(
        extract_skills("\n".join(sections["preferred"]))
    )

    preferred_skills -= required_skills

    return {
        "required": sorted(required_skills),
        "preferred": sorted(preferred_skills),
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