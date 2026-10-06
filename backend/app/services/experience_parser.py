import re


MONTHS = (
    "jan|january|feb|february|mar|march|apr|april|"
    "may|jun|june|jul|july|aug|august|sep|sept|"
    "september|oct|october|nov|november|dec|december"
)


DATE_RANGE_PATTERN = re.compile(
    rf"""
    (?:
        {MONTHS}
    )
    \.?
    \s*
    ,?
    \s*
    \d{{4}}
    \s*
    (?:-|–|—|to)
    \s*
    (?:
        {MONTHS}
    )
    \.?
    \s*
    ,?
    \s*
    (?:
        \d{{4}}|present|current
    )
    """,
    re.IGNORECASE | re.VERBOSE
)


JOB_TITLE_KEYWORDS = [
    "developer",
    "engineer",
    "intern",
    "analyst",
    "designer",
    "manager",
    "consultant",
    "software",
    "frontend",
    "backend",
    "full stack",
    "data scientist",
    "data analyst"
]


COMPANY_KEYWORDS = [
    "technologies",
    "technology",
    "solutions",
    "systems",
    "services",
    "company",
    "corporation",
    "inc",
    "ltd",
    "pvt",
    "llp",
    "labs",
    "studio",
    "samurai"
]


def clean_line(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text.strip()
    )


def is_date_range(text: str) -> bool:
    """
    Check whether a line contains a date range.
    """

    return bool(
        DATE_RANGE_PATTERN.search(text)
    )


def looks_like_job_title(text: str) -> bool:
    """
    Detect likely job titles.
    """

    text_lower = text.lower().strip()

    return any(
        keyword in text_lower
        for keyword in JOB_TITLE_KEYWORDS
    )


def looks_like_company(text: str) -> bool:
    """
    Detect likely company names.
    """

    text_lower = text.lower()

    return any(
        keyword in text_lower
        for keyword in COMPANY_KEYWORDS
    )


def extract_experience_entries(
    experience_text: str
) -> list[dict]:

    lines = [
        clean_line(line)
        for line in experience_text.splitlines()
        if clean_line(line)
    ]

    entries = []

    i = 0

    while i < len(lines):

        line = lines[i]

        # --------------------------------------------------
        # Pattern 1:
        #
        # Job Title
        # Date
        # Company
        # --------------------------------------------------

        if looks_like_job_title(line):

            job_title = line
            duration = ""
            company = None

            if (
                i + 1 < len(lines)
                and is_date_range(lines[i + 1])
            ):
                duration = lines[i + 1]

            if (
                i + 2 < len(lines)
                and not looks_like_job_title(lines[i + 2])
                and not is_date_range(lines[i + 2])
            ):
                company = lines[i + 2]

            entries.append({
                "job_title": job_title,
                "company": company,
                "duration": duration,
                "description": "",
                "confidence": (
                    "high"
                    if duration and company
                    else "medium"
                )
            })

            i += 3
            continue

        # --------------------------------------------------
        # Pattern 2:
        #
        # Date
        # Company
        # Job Title
        #
        # This can happen because of PDF column layout.
        # --------------------------------------------------

        if is_date_range(line):

            duration = line
            company = None
            job_title = None

            if i + 1 < len(lines):
                possible_company = lines[i + 1]

                if not looks_like_job_title(
                    possible_company
                ):
                    company = possible_company

            if i + 2 < len(lines):
                possible_title = lines[i + 2]

                if looks_like_job_title(
                    possible_title
                ):
                    job_title = possible_title

            if job_title:

                entries.append({
                    "job_title": job_title,
                    "company": company,
                    "duration": duration,
                    "description": "",
                    "confidence": (
                        "high"
                        if company
                        else "medium"
                    )
                })

                i += 3
                continue

        i += 1

    return entries