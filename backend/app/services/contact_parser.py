import re


def clean_contact_text(text: str) -> str:
    """
    Clean common PDF/OCR artifacts while preserving useful contact data.
    """
    if not text:
        return ""

    text = text.replace("\u00a0", " ")
    text = text.replace("©", " ")
    text = text.replace("&", " ")

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)

    return text.strip()


def extract_email(text: str):
    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text
    )
    return match.group(0) if match else None


def extract_phone(text: str):
    """
    Extract Indian/international phone numbers even when PDF extraction
    inserts spaces inside the number.
    """

    # First normalize spaces around digit sequences
    candidates = re.findall(
        r"(?:\+?\d[\d\s().-]{8,}\d)",
        text
    )

    for candidate in candidates:
        digits = re.sub(r"\D", "", candidate)

        # Indian mobile number
        if len(digits) == 10 and digits[0] in "6789":
            return digits

        # Indian number with country code
        if len(digits) == 12 and digits.startswith("91"):
            return "+" + digits

        # Generic international number
        if 10 <= len(digits) <= 15:
            return "+" + digits

    return None


def extract_name(text: str):
    """
    Usually the candidate name is near the beginning of the resume.
    """
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    ignored = {
        "resume",
        "cv",
        "curriculum vitae",
        "contact",
        "summary",
        "profile",
        "undergrad student",
        "student",
    }

    for line in lines[:10]:
        cleaned = re.sub(r"[^A-Za-z .'-]", "", line).strip()

        if not cleaned:
            continue

        if cleaned.lower() in ignored:
            continue

        # Avoid sentences
        if len(cleaned.split()) <= 5:
            return cleaned.upper()

    return None




def extract_location(text: str):
    """Extract labelled or unlabelled locations from resume contact lines."""

    # Strategy 1: Explicitly labelled location or address.
    match = re.search(
        r"(?:location|address)\s*[:\-]\s*([^\n]+)",
        text,
        flags=re.IGNORECASE
    )

    if match:
        location = match.group(1).strip()
        location = re.split(
            r"\b(?:nationality|age|phone|email|linkedin|github)\b",
            location,
            flags=re.IGNORECASE
        )[0].strip(" ,:-|")

        if location:
            return location

    # Strategy 2: Split early resume lines into contact fields.
    for line in text.splitlines()[:15]:
        parts = re.split(r"\s*[|•]\s*", line.strip())

        for part in parts:
            candidate = part.strip(" ,:-|")

            if not re.fullmatch(
                r"[A-Za-z .'-]+,\s*[A-Za-z .'-]+",
                candidate
            ):
                continue

            lowered = candidate.lower()

            if any(word in lowered for word in (
                "linkedin", "github", "university", "college",
                "email", "phone", "software developer",
                "computer science"
            )):
                continue

            return candidate

    return None


def extract_github(text: str):
    """Extract a GitHub profile URL."""
    match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+",
        text,
        flags=re.IGNORECASE
    )

    return match.group(0) if match else None


def extract_linkedin(text: str):
    """Extract LinkedIn URLs even when a PDF splits them across lines."""

    normalized = re.sub(r"\s+", "", text)

    match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/"
        r"[A-Za-z0-9_-]+/?",
        normalized,
        flags=re.IGNORECASE
    )

    return match.group(0) if match else None


def extract_contact_information(text: str):
    """
    Extract basic contact information from resume text.
    """

    cleaned_text = clean_contact_text(text)

    return {
        "name": extract_name(cleaned_text),
        "email": extract_email(cleaned_text),
        "phone": extract_phone(cleaned_text),
        "location": extract_location(cleaned_text),
        "linkedin": extract_linkedin(cleaned_text),
        "github": extract_github(cleaned_text),
    }