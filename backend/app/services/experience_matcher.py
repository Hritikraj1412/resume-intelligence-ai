import re
from datetime import datetime


MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def parse_date(text: str):
    """
    Convert strings such as:
    Dec, 2025
    July 2026
    into datetime objects.
    """

    if not text:
        return None

    cleaned = text.lower().strip()

    cleaned = cleaned.replace(",", " ")

    match = re.search(
        r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
        r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|"
        r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{4})",
        cleaned
    )

    if not match:
        return None

    month_text = match.group(1)
    year = int(match.group(2))

    month = MONTHS.get(month_text)

    if not month:
        return None

    return datetime(year, month, 1)


def calculate_duration_years(duration: str) -> float:
    """
    Calculate approximate experience duration from a date range.

    Examples:
    Dec, 2025 - Jan, 2026
    July, 2026 - Aug, 2026
    """

    if not duration:
        return 0.0

    match = re.search(
        r"(.+?)\s*(?:-|–|—|to)\s*(.+)",
        duration,
        re.IGNORECASE
    )

    if not match:
        return 0.0

    start_text = match.group(1).strip()
    end_text = match.group(2).strip()

    start_date = parse_date(start_text)

    if not start_date:
        return 0.0

    if end_text.lower() in {"present", "current"}:
        end_date = datetime.now()
    else:
        end_date = parse_date(end_text)

    if not end_date:
        return 0.0

    months = (
        (end_date.year - start_date.year) * 12
        + (end_date.month - start_date.month)
    )

    if months < 0:
        return 0.0

    # Count the starting month as part of the experience.
    months += 1

    return round(months / 12, 2)


def extract_required_years(text: str) -> float:
    """
    Extract the upper bound of a required experience range.

    Example:
    1-2 years -> 2
    2+ years  -> 2
    """

    if not text:
        return 0.0

    range_match = re.search(
        r"(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)",
        text,
        re.IGNORECASE
    )

    if range_match:
        return float(range_match.group(2))

    plus_match = re.search(
        r"(\d+)\+?\s*(?:years?|yrs?)",
        text,
        re.IGNORECASE
    )

    if plus_match:
        return float(plus_match.group(1))

    return 0.0


def calculate_experience_match(
    resume_experience: list[dict],
    required_experience: str | None
) -> dict:

    if not required_experience:
       return {
        "score": None,
        "resume_years": 0.0,
        "required_years": 0.0,
        "status": "not_required"
    }

    required_years = extract_required_years(
        required_experience
    )

    if required_years == 0:
        return {
            "score": 0.0,
            "resume_years": 0.0,
            "required_years": 0.0,
            "status": "unknown"
        }

    resume_years = 0.0

    for experience in resume_experience:

        duration = experience.get(
            "duration",
            ""
        )

        resume_years += calculate_duration_years(
            duration
        )

    if resume_years >= required_years:

        score = 100.0
        status = "meets_requirement"

    elif resume_years > 0:

        score = (
            resume_years /
            required_years
        ) * 100

        status = "partially_meets"

    else:

        score = 0.0
        status = "no_experience_detected"

    return {
        "score": round(
            min(score, 100.0),
            2
        ),
        "resume_years": round(
            resume_years,
            2
        ),
        "required_years": required_years,
        "status": status
    }