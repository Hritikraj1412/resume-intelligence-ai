import re


SECTION_ALIASES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "about me",
        "about",
        "objective",
        "career objective",
        "professional profile"
    ],

    "skills": [
        "skills",
        "skill",
        "technical skills",
        "technical skill",
        "core skills",
        "key skills",
        "technologies",
        "technical expertise",
        "technical knowledge"
    ],

    "experience": [
        "experience",
        "experiences",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
        "internship",
        "internships"
    ],

    "education": [
        "education",
        "educational background",
        "academic background",
        "academic qualifications",
        "qualification",
        "qualifications"
    ],

    "projects": [
        "projects",
        "project",
        "personal projects",
        "academic projects",
        "key projects",
        "major projects",
        "project experience"
    ],

    "certifications": [
        "certifications",
        "certification",
        "certificates",
        "certificate",
        "licenses",
        "courses",
        "training"
    ],

    "achievements": [
        "achievements",
        "achievement",
        "accomplishments",
        "awards",
        "honors",
        "honours"
    ],

    "languages": [
        "languages",
        "language"
    ]
}


def normalize_heading(text: str) -> str:
    """
    Normalize a possible resume heading.
    """

    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9+#.&\s-]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def detect_section_heading(line: str):
    """
    Detect whether a line is a known resume section heading.
    """

    normalized = normalize_heading(line)

    if not normalized:
        return None

    for section, aliases in SECTION_ALIASES.items():

        for alias in aliases:

            if normalized == alias:
                return section

    return None


def looks_like_heading(line: str) -> bool:
    """
    Detect headings written mostly in uppercase.
    """

    stripped = line.strip()

    if not stripped:
        return False

    if len(stripped) > 40:
        return False

    letters = [
        char
        for char in stripped
        if char.isalpha()
    ]

    if not letters:
        return False

    uppercase_count = sum(
        char.isupper()
        for char in letters
    )

    uppercase_ratio = (
        uppercase_count / len(letters)
    )

    return uppercase_ratio >= 0.85


def extract_resume_sections(text: str) -> dict:
    """
    Split extracted resume text into logical sections.
    """

    sections = {
        "summary": "",
        "skills": "",
        "experience": "",
        "education": "",
        "projects": "",
        "certifications": "",
        "achievements": "",
        "languages": "",
        "other": ""
    }

    current_section = "other"

    pre_section_content = []

    lines = text.splitlines()

    for line in lines:

        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        detected_section = detect_section_heading(
            cleaned_line
        )

        if detected_section:

            current_section = detected_section

            continue

        if (
            current_section == "other"
            and looks_like_heading(cleaned_line)
        ):
            continue

        if current_section == "other":

            pre_section_content.append(
                cleaned_line
            )

        else:

            sections[current_section] += (
                cleaned_line + "\n"
            )

    # Content before the first detected section
    # is treated as the summary/header area.
    if pre_section_content:

        sections["summary"] = "\n".join(
            pre_section_content
        )

    for section in sections:

        sections[section] = (
            sections[section].strip()
        )

    return sections