
import re


MONTHS = (
    r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
    r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
    r"sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
)

MONTH_YEAR = rf"(?:{MONTHS})\.?\s*,?\s*\d{{4}}"
NUMERIC_DATE = r"(?:0?[1-9]|1[0-2])[/.-]\d{4}"
YEAR = r"\d{4}"
DATE_POINT = rf"(?:{MONTH_YEAR}|{NUMERIC_DATE}|{YEAR}|present|current|now)"

DATE_RANGE_PATTERN = re.compile(
    rf"^\s*({DATE_POINT})\s*(?:-|–|—|\bto\b)\s*({DATE_POINT})\s*$",
    re.IGNORECASE,
)

JOB_TITLE_KEYWORDS = [
    "developer", "engineer", "intern", "analyst", "designer",
    "manager", "consultant", "software", "frontend", "front-end",
    "backend", "back-end", "full stack", "full-stack",
    "data scientist", "data analyst", "programmer", "tester",
    "qa", "quality assurance", "administrator", "architect",
    "technician", "accountant", "researcher", "trainee",
    "devops", "product owner", "product manager",
]

COMPANY_KEYWORDS = [
    "technologies", "technology", "solutions", "systems",
    "services", "company", "corporation", "inc", "ltd",
    "pvt", "llp", "labs", "studio", "samurai", "india",
]

SECTION_HEADERS = {
    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "internships",
}

DESCRIPTION_STARTERS = (
    "developed ", "built ", "created ", "worked ",
    "responsible for ", "designed ", "implemented ",
    "managed ", "assisted ", "maintained ", "worked on ",
    "using ", "helped ", "contributed ",
)


def clean_line(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def is_date_range(text: str) -> bool:
    return bool(DATE_RANGE_PATTERN.fullmatch(clean_line(text)))


def looks_like_job_title(text: str) -> bool:
    value = clean_line(text).lower()
    return any(keyword in value for keyword in JOB_TITLE_KEYWORDS)


def looks_like_company(text: str) -> bool:
    value = clean_line(text).lower()
    return any(keyword in value for keyword in COMPANY_KEYWORDS)


def is_description(text: str) -> bool:
    value = clean_line(text).lower()
    return value.startswith(DESCRIPTION_STARTERS)


def split_title_company(line: str) -> tuple[str, str | None]:
    """Split common 'Job Title | Company' or 'Job Title at Company' lines."""
    parts = re.split(r"\s+\|\s+|\s+@\s+|\s+at\s+", clean_line(line), maxsplit=1, flags=re.IGNORECASE)

    if len(parts) == 2 and looks_like_job_title(parts[0]):
        return parts[0].strip(), parts[1].strip()

    return clean_line(line), None


def extract_experience_entries(experience_text: str) -> list[dict]:
    """Extract dated work and internship entries from line-based resume layouts."""
    lines = [
        clean_line(line)
        for line in experience_text.splitlines()
        if clean_line(line)
    ]

    entries = []

    for i, line in enumerate(lines):
        if line.lower() in SECTION_HEADERS or is_date_range(line):
            continue

        job_title, inline_company = split_title_company(line)

        if not looks_like_job_title(job_title):
            continue

        # Find a nearby date range, preferably after the title.
        date_index = None
        for j in range(i + 1, min(i + 4, len(lines))):
            if is_date_range(lines[j]):
                date_index = j
                break

            # Stop if another likely job title starts first.
            if looks_like_job_title(split_title_company(lines[j])[0]):
                break

        # Also support date -> title layouts.
        if date_index is None:
            for j in range(max(0, i - 3), i):
                if is_date_range(lines[j]):
                    date_index = j
                    break

        if date_index is None:
            continue

        company = inline_company
        description_lines = []

        # If company is not inline, inspect nearby lines for a plausible company.
        if not company:
            candidate_indices = (
                list(range(date_index + 1, min(date_index + 3, len(lines)))
                     if date_index < i else range(i + 1, min(i + 3, len(lines))))
            )

            for j in candidate_indices:
                candidate = lines[j]

                if j == i or is_date_range(candidate):
                    continue

                if candidate.lower() in SECTION_HEADERS:
                    continue

                if looks_like_job_title(split_title_company(candidate)[0]):
                    continue

                if is_description(candidate):
                    description_lines.append(candidate)
                    continue

                if looks_like_company(candidate) or (
                    date_index < i and j < i
                ):
                    company = candidate
                    break

        # Collect nearby description text without crossing into another entry.
        for j in range(date_index + 1, len(lines)):
            candidate = lines[j]

            if candidate.lower() in SECTION_HEADERS or is_date_range(candidate):
                break

            candidate_title, candidate_company = split_title_company(candidate)
            if looks_like_job_title(candidate_title):
                break

            if candidate == company:
                continue

            if is_description(candidate):
                description_lines.append(candidate)

        entries.append({
            "job_title": job_title,
            "company": company,
            "duration": lines[date_index],
            "description": " ".join(dict.fromkeys(description_lines)),
            "confidence": "high" if company else "medium",
        })

    # Remove duplicate title/date/company combinations.
    unique_entries = []
    seen = set()

    for entry in entries:
        key = (
            entry["job_title"].lower(),
            entry["duration"].lower(),
            (entry["company"] or "").lower(),
        )
        if key not in seen:
            seen.add(key)
            unique_entries.append(entry)

    return unique_entries