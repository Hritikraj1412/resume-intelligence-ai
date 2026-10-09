
import re


# =========================================================
# SECTION ALIASES
# =========================================================

SECTION_ALIASES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "about me",
        "about",
        "objective",
        "career objective",
        "career profile",
        "personal profile",
        "professional objective",
    ],
    "skills": [
        "skills",
        "skill",
        "technical skills",
        "technical skill",
        "core skills",
        "key skills",
        "technical expertise",
        "technical knowledge",
        "areas of expertise",
        "competencies",
        "core competencies",
        "professional skills",
        "skills and competencies",
        "technical competencies",
        "technologies",
        "tools and technologies",
    ],
    "experience": [
        "experience",
        "experiences",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
        "career history",
        "professional history",
        "work profile",
        "internship",
        "internships",
        "internship experience",
        "internship history",
        "career experience",
    ],
    "education": [
        "education",
        "educational background",
        "educational qualification",
        "educational qualifications",
        "academic background",
        "academic qualification",
        "academic qualifications",
        "academic history",
        "academic profile",
        "qualification",
        "qualifications",
        "education qualification",
        "educational details",
        "academic details",
    ],
    "projects": [
        "projects",
        "project",
        "personal projects",
        "academic projects",
        "key projects",
        "major projects",
        "project experience",
        "selected projects",
        "featured projects",
        "academic project",
        "personal project",
    ],
    "certifications": [
        "certifications",
        "certification",
        "certificates",
        "certificate",
        "licenses",
        "licences",
        "courses",
        "training",
        "professional certifications",
        "courses and certifications",
    ],
    "achievements": [
        "achievements",
        "achievement",
        "accomplishments",
        "awards",
        "award",
        "honors",
        "honours",
        "recognition",
        "recognitions",
        "accomplishments and awards",
    ],
    "languages": [
        "languages",
        "language",
        "languages known",
        "language skills",
        "spoken languages",
        "linguistic skills",
    ],
    "personal": [
        "personal details",
        "personal information",
        "personal profile",
        "additional information",
        "other information",
        "basic information",
    ],
}


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_heading(text: str) -> str:
    """Normalize a possible resume heading."""
    text = text.lower().strip()

    # Remove bullets and decorative characters.
    text = re.sub(r"^[•●▪◦■◆★✓✔\-\*]+\s*", "", text)

    # Remove punctuation except useful heading characters.
    text = re.sub(r"[^a-z0-9+#.&\s-]", "", text)

    # Normalize separators and whitespace.
    text = text.replace("&", " and ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================================================
# HEADING DETECTION
# =========================================================

def detect_section_heading(line: str):
    """Detect a known resume section heading."""
    normalized = normalize_heading(line)

    if not normalized:
        return None

    for section, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if normalized == alias:
                return section

    return None


# =========================================================
# GENERIC HEADING DETECTION
# =========================================================


def looks_like_heading(line: str) -> bool:
    """Detect section headings without treating job titles as headings."""
    stripped = line.strip()

    if not stripped or len(stripped) > 45:
        return False

    lowered = normalize_heading(stripped)

    # A job title must never be treated as a section heading.
    job_title_terms = (
        "developer", "engineer", "intern", "analyst", "designer",
        "programmer", "tester", "consultant", "technician",
        "administrator", "architect", "trainee", "scientist",
        "accountant", "manager", "devops", "product owner",
    )

    if any(
        re.search(rf"\b{re.escape(term)}\b", lowered)
        for term in job_title_terms
    ):
        return False

    letters = [char for char in stripped if char.isalpha()]

    if not letters:
        return False

    uppercase_ratio = (
        sum(char.isupper() for char in letters) / len(letters)
    )

    # All-caps headings, such as SKILLS or EXPERIENCE.
    if uppercase_ratio >= 0.85:
        return True

    # Do not classify ordinary title-case content as headings.
    return False


# =========================================================
# HEADING NORMALIZATION HELPERS
# =========================================================

def infer_section_from_heading(line: str):
    """Infer a section from a heading not listed as an exact alias."""
    normalized = normalize_heading(line)

    if not normalized:
        return None

    # Education.
    if any(
        keyword in normalized
        for keyword in (
            "education",
            "educational",
            "academic",
            "qualification",
        )
    ):
        return "education"

    # Experience.
    if any(
        keyword in normalized
        for keyword in (
            "experience",
            "employment",
            "work history",
            "career history",
            "internship",
        )
    ):
        return "experience"

    # Skills.
    if any(
        keyword in normalized
        for keyword in (
            "skill",
            "competenc",
            "expertise",
            "technolog",
        )
    ):
        return "skills"

    # Projects.
    if "project" in normalized:
        return "projects"

    # Certifications.
    if any(
        keyword in normalized
        for keyword in (
            "certification",
            "certificate",
            "license",
            "course",
            "training",
        )
    ):
        return "certifications"

    # Achievements.
    if any(
        keyword in normalized
        for keyword in (
            "achievement",
            "award",
            "honor",
            "accomplishment",
            "recognition",
        )
    ):
        return "achievements"

    # Languages.
    if any(
        keyword in normalized
        for keyword in (
            "language",
            "linguistic",
        )
    ):
        return "languages"

    # Personal information.
    if any(
        keyword in normalized
        for keyword in (
            "personal detail",
            "personal information",
            "basic information",
        )
    ):
        return "personal"

    # Summary.
    if any(
        keyword in normalized
        for keyword in (
            "summary",
            "profile",
            "objective",
            "about",
        )
    ):
        return "summary"

    return None


# =========================================================
# MAIN SECTION EXTRACTION
# =========================================================

def extract_resume_sections(text: str) -> dict:
    """
    Split extracted resume text into logical sections.

    Supports standard headings, alternate section names,
    uppercase headings, decorated headings, and varied ordering.
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
        "personal": "",
        "other": "",
    }

    current_section = "other"
    pre_section_content = []

    for line in text.splitlines():
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        # Exact known heading.
        detected_section = detect_section_heading(cleaned_line)

        if detected_section:
            current_section = detected_section
            continue

        # Generic heading detection and inference.
        if looks_like_heading(cleaned_line):
            inferred_section = infer_section_from_heading(cleaned_line)

            if inferred_section:
                current_section = inferred_section
                continue

            # Preserve unknown headings instead of discarding them.
            if current_section == "other":
                pre_section_content.append(cleaned_line)
            else:
                sections[current_section] += cleaned_line + "\n"

            continue

        # Store content in the active section.
        if current_section == "other":
            pre_section_content.append(cleaned_line)
        else:
            sections[current_section] += cleaned_line + "\n"

    # Header / pre-section content.
    if pre_section_content:
        sections["summary"] = "\n".join(pre_section_content)

    # Clean all sections.
    for section in sections:
        sections[section] = sections[section].strip()

    return sections