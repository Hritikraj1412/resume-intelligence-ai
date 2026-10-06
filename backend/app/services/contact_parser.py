import re


# --------------------------------------------------
# EMAIL
# --------------------------------------------------

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)


# --------------------------------------------------
# PHONE
# --------------------------------------------------

PHONE_PATTERN = re.compile(
    r"(?<!\d)"
    r"(?:\+91[\s-]?)?"
    r"[6-9]\d{9}"
    r"(?!\d)"
)


# --------------------------------------------------
# LINKEDIN
# --------------------------------------------------

LINKEDIN_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9._-]+",
    re.IGNORECASE
)


# --------------------------------------------------
# GITHUB
# --------------------------------------------------

GITHUB_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9._-]+",
    re.IGNORECASE
)


def extract_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)

    if match:
        return match.group(0)

    return None


def extract_phone(text: str) -> str | None:
    match = PHONE_PATTERN.search(text)

    if match:
        return match.group(0)

    return None


def extract_linkedin(text: str) -> str | None:
    match = LINKEDIN_PATTERN.search(text)

    if match:
        return match.group(0)

    return None


def extract_github(text: str) -> str | None:
    match = GITHUB_PATTERN.search(text)

    if match:
        return match.group(0)

    return None


def extract_name(text: str) -> str | None:

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return None

    # Look at the first few lines because
    # the candidate's name is normally near
    # the top of a resume.

    for line in lines[:8]:

        # Ignore obvious contact information
        if EMAIL_PATTERN.search(line):
            continue

        if PHONE_PATTERN.search(line):
            continue

        if LINKEDIN_PATTERN.search(line):
            continue

        if GITHUB_PATTERN.search(line):
            continue

        # Ignore common resume titles
        if line.lower() in {
            "resume",
            "curriculum vitae",
            "cv",
            "full stack developer",
            "software developer",
            "web developer",
            "computer science student"
        }:
            continue

        # A name normally contains letters/spaces
        # and is relatively short.

        if (
            2 <= len(line.split()) <= 5
            and len(line) <= 60
            and re.fullmatch(
                r"[A-Za-z][A-Za-z .'-]*",
                line
            )
        ):
            return line

    return None


def extract_location(text: str) -> str | None:

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    location_keywords = [
        "ahmedabad",
        "gujarat",
        "delhi",
        "mumbai",
        "pune",
        "bangalore",
        "bengaluru",
        "hyderabad",
        "chennai",
        "kolkata",
        "jaipur",
        "surat",
        "vadodara"
    ]

    for line in lines[:15]:

        line_lower = line.lower()

        if any(
            keyword in line_lower
            for keyword in location_keywords
        ):
            return line

    return None


def extract_contact_information(text: str) -> dict:

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "location": extract_location(text),
        "linkedin": extract_linkedin(text),
        "github": extract_github(text)
    }