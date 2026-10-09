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
    """Parse common resume date formats into datetime objects."""
    if not text:
        return None

    cleaned = text.lower().strip().replace(",", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Month and year: Jan 2025, January 2025, July 2026
    month_match = re.search(
        r"\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
        r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
        r"sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|"
        r"dec(?:ember)?)\.?\s+(\d{4})\b",
        cleaned,
        re.IGNORECASE,
    )

    if month_match:
        month_text = month_match.group(1).lower()
        year = int(month_match.group(2))
        month = MONTHS.get(month_text)
        return datetime(year, month, 1) if month else None

    # Numeric month/year: 01/2025, 06-2025, 12.2025
    numeric_match = re.search(
        r"\b(0?[1-9]|1[0-2])[/.-](\d{4})\b",
        cleaned,
    )

    if numeric_match:
        return datetime(
            int(numeric_match.group(2)),
            int(numeric_match.group(1)),
            1,
        )

    # Year only: 2024, 2025
    year_match = re.fullmatch(r"\d{4}", cleaned)

    if year_match:
        return datetime(int(cleaned), 1, 1)

    return None


def calculate_duration_years(duration: str) -> float:
    """Calculate elapsed experience from a date range."""

    if not duration:
        return 0.0

    match = re.search(
        r"(.+?)\s*(?:-|–|—|\bto\b)\s*(.+)",
        duration.strip(),
        re.IGNORECASE
    )

    if not match:
        return 0.0

    start_text = match.group(1).strip()
    end_text = match.group(2).strip()

    start_date = parse_date(start_text)

    if not start_date:
        return 0.0

    if end_text.lower() in {"present", "current", "now"}:
        end_date = datetime.now()
    else:
        end_date = parse_date(end_text)

    if not end_date or end_date < start_date:
        return 0.0

    # Month-level dates cannot establish exact days.
    # Use the difference between calendar months, without
    # automatically counting the ending month as a full month.
    months = (
        (end_date.year - start_date.year) * 12
        + (end_date.month - start_date.month)
    )

    return round(months / 12, 2)




def extract_required_years_range(text: str) -> tuple[float, float]:
    """
    Extract minimum and maximum years from an experience requirement.

    Examples:
    '1-2 years' -> (1.0, 2.0)
    '2+ years'  -> (2.0, float('inf'))
    '1 year'    -> (1.0, 1.0)
    """

    if not text:
        return 0.0, 0.0

    normalized = text.lower().strip().replace("–", "-").replace("—", "-")

    range_match = re.search(
        r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
        normalized,
    )

    if range_match:
        minimum = float(range_match.group(1))
        maximum = float(range_match.group(2))

        if maximum >= minimum:
            return minimum, maximum

        return maximum, minimum

    plus_match = re.search(
        r"(\d+(?:\.\d+)?)\s*\+\s*(?:years?|yrs?)",
        normalized,
    )

    if plus_match:
        return float(plus_match.group(1)), float("inf")

    single_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
        normalized,
    )

    if single_match:
        years = float(single_match.group(1))
        return years, years

    return 0.0, 0.0

def calculate_total_experience_years(resume_experience: list[dict]) -> float:
    """Calculate total elapsed experience without double-counting overlaps."""
    intervals = []

    for item in resume_experience:
        duration = item.get("duration", "")
        if not duration:
            continue

        match = re.search(
            r"(.+?)\s*(?:-|–|—|\bto\b)\s*(.+)",
            duration.strip(),
            re.IGNORECASE,
        )
        if not match:
            continue

        start_date = parse_date(match.group(1).strip())
        end_text = match.group(2).strip()

        if not start_date:
            continue

        
        if end_text.lower() in {"present", "current", "now"}:
            end_date = datetime.now()
        else:
            end_date = parse_date(end_text)

        if not end_date or end_date < start_date:
            continue

        # Never credit experience beyond the current date.
        now = datetime.now()
        current_month = now.year * 12 + now.month - 1
        start_month = start_date.year * 12 + start_date.month - 1
        end_month = end_date.year * 12 + end_date.month - 1

        if start_month > current_month:
           continue

        
        end_month = min(end_month, current_month)

        if end_month <= start_month:
            continue

        # Keep the capped end_month; do not recalculate it
        # from the original end_date.
        intervals.append((start_month, end_month))

    if not intervals:
        return 0.0

    intervals.sort()
    total_months = 0
    current_start, current_end = intervals[0]

    for start, end in intervals[1:]:
        if start <= current_end:
            # Overlapping or adjacent intervals: merge them.
            current_end = max(current_end, end)
        else:
            total_months += current_end - current_start
            current_start, current_end = start, end

    total_months += current_end - current_start

    return round(total_months / 12, 2)



def calculate_experience_match(
    resume_experience: list[dict],
    required_experience: str | None
) -> dict:
    """Compare candidate experience against a requirement range."""

    resume_years = calculate_total_experience_years(resume_experience)

    if not required_experience:
        return {
            "score": None,
            "resume_years": resume_years,
            "required_years": None,
            "minimum_required_years": None,
            "maximum_required_years": None,
            "status": "not_required",
            "explanation": "The job does not specify an experience requirement."
        }

    minimum_years, maximum_years = extract_required_years_range(
        required_experience
    )

    if minimum_years == 0 and maximum_years == 0:
        return {
            "score": None,
            "resume_years": resume_years,
            "required_years": 0.0,
            "minimum_required_years": None,
            "maximum_required_years": None,
            "status": "not_required",
            "explanation": "The experience requirement could not be interpreted."
        }

    if resume_years >= maximum_years:
        score = 100.0
        status = "meets_requirement"
        explanation = (
            f"You have {resume_years:.2f} years of experience, "
            "meeting or exceeding the stated range."
        )
    elif resume_years >= minimum_years:
        score = 100.0
        status = "meets_minimum"
        explanation = (
            f"You have {resume_years:.2f} years of experience. "
            "You meet the minimum requirement but are below the "
            "upper end of the stated range."
        )
    elif resume_years > 0:
        score = (resume_years / minimum_years) * 100
        status = "partially_meets"
        explanation = (
            f"You have {resume_years:.2f} years of experience, "
            f"below the minimum requirement of {minimum_years:.2f} years."
        )
    else:
        score = 0.0
        status = "no_experience_detected"
        explanation = (
            f"No dated experience was detected. The minimum requirement "
            f"is {minimum_years:.2f} years."
        )

    return {
        "score": round(min(max(score, 0.0), 100.0), 2),
        "resume_years": resume_years,
        "required_years": minimum_years,
        "minimum_required_years": minimum_years,
        "maximum_required_years": (
            maximum_years if maximum_years != float("inf") else None
        ),
        "status": status,
        "explanation": explanation
    }