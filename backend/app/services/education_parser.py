import re


YEAR_RANGE_PATTERN = re.compile(
    r"\b((?:19|20)\d{2})\s*(?:-|–|—|to)\s*((?:19|20)\d{2})\b",
    re.IGNORECASE
)

SINGLE_YEAR_PATTERN = re.compile(
    r"\b(?:19|20)\d{2}\b"
)


DEGREE_KEYWORDS = [
    "bachelor",
    "master",
    "b.tech",
    "m.tech",
    "b.e",
    "m.e",
    "bca",
    "mca",
    "b.sc",
    "m.sc",
    "bba",
    "mba",
    "phd",
    "diploma",
    "degree",
    "higher secondary",
    "secondary certificate",
    "secondary school",
    "hsc",
    "ssc",
]


INSTITUTION_KEYWORDS = [
    "university",
    "college",
    "institute",
    "school",
    "academy",
    "iit",
    "nit",
]


def clean_line(text: str) -> str:
    text = text.strip()

    # Remove common PDF/OCR bullets
    text = re.sub(r"^[*•▪◦●○\-]+\s*", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_year_range(text: str):
    match = YEAR_RANGE_PATTERN.search(text)

    if not match:
        return None, None

    return int(match.group(1)), int(match.group(2))


def extract_single_year(text: str):
    match = SINGLE_YEAR_PATTERN.search(text)

    if match:
        return int(match.group(0))

    return None


def looks_like_degree(text: str) -> bool:

    text_lower = text.lower()

    return any(
        keyword in text_lower
        for keyword in DEGREE_KEYWORDS
    )


def looks_like_institution(text: str) -> bool:

    text_lower = text.lower()

    return any(
        keyword in text_lower
        for keyword in INSTITUTION_KEYWORDS
    )


def is_score_line(text: str) -> bool:

    text_lower = text.lower()

    return any(
        keyword in text_lower
        for keyword in [
            "cgpa",
            "percentage",
            "percent",
            "gpa",
            "grade",
            "score"
        ]
    )


def clean_degree(text: str) -> str:

    text = clean_line(text)

    # Keep useful "Pursuing" information
    text = re.sub(
        r"\s*\(\s*semester\s+\d+\s*-\s*",
        " (",
        text,
        flags=re.IGNORECASE
    )

    return text


def clean_institution(text: str) -> str:

    text = clean_line(text)

    return text


def build_entry(
    degree=None,
    institution=None,
    start_year=None,
    end_year=None,
    description_lines=None,
    confidence="medium"
):

    description_lines = description_lines or []

    return {
        "degree": degree,
        "institution": institution,
        "start_year": start_year,
        "end_year": end_year,
        "description": " ".join(description_lines).strip(),
        "confidence": confidence
    }


def extract_year_based_entries(lines: list[str]) -> list[dict]:

    entries = []

    i = 0

    while i < len(lines):

        line = lines[i]

        if YEAR_RANGE_PATTERN.search(line):

            start_year, end_year = extract_year_range(line)

            degree = None
            institution = None

            if i + 1 < len(lines):

                possible_degree = lines[i + 1]

                if looks_like_degree(possible_degree):
                    degree = clean_degree(possible_degree)

            if i + 2 < len(lines):

                possible_institution = lines[i + 2]

                if (
                    looks_like_institution(possible_institution)
                    or not looks_like_degree(possible_institution)
                ):
                    institution = clean_institution(
                        possible_institution
                    )

            description_lines = []

            for description_line in lines[i + 3:]:

                if looks_like_degree(description_line):
                    break

                description_lines.append(
                    description_line
                )

            entries.append(
                build_entry(
                    degree=degree,
                    institution=institution,
                    start_year=start_year,
                    end_year=end_year,
                    description_lines=description_lines,
                    confidence=(
                        "high"
                        if degree and institution
                        else "medium"
                    )
                )
            )

            i += 1
            continue

        i += 1

    return entries


def extract_degree_block_entries(
    lines: list[str]
) -> list[dict]:

    entries = []

    i = 0

    while i < len(lines):

        line = lines[i]

        if not looks_like_degree(line):
            i += 1
            continue

        degree = clean_degree(line)

        institution = None
        description_lines = []

        # Look ahead for institution
        if i + 1 < len(lines):

            next_line = lines[i + 1]

            if looks_like_institution(next_line):

                institution = clean_institution(next_line)

                i += 1

        # Look for score / CGPA / percentage
        j = i + 1

        while j < len(lines):

            current = lines[j]

            # A new degree means current entry is finished
            if looks_like_degree(current):

                break

            if is_score_line(current):

                description_lines.append(current)

            j += 1

        confidence = "medium"

        if degree and institution:
            confidence = "high"

        entries.append(
            build_entry(
                degree=degree,
                institution=institution,
                description_lines=description_lines,
                confidence=confidence
            )
        )

        i = max(j, i + 1)

    return entries


def remove_duplicate_entries(
    entries: list[dict]
) -> list[dict]:

    unique = []

    seen = set()

    for entry in entries:

        key = (
            (entry.get("degree") or "").lower(),
            (entry.get("institution") or "").lower()
        )

        if key in seen:
            continue

        seen.add(key)
        unique.append(entry)

    return unique

def extract_single_line_education_entries(
    lines: list[str]
) -> list[dict]:
    entries = []

    for line in lines:
        year_match = YEAR_RANGE_PATTERN.search(line)

        if not year_match or not looks_like_degree(line):
            continue

        start_year, end_year = extract_year_range(line)

        # Separate the degree from the institution.
        parts = re.split(r"\s+[—–]\s+", line, maxsplit=1)

        if len(parts) != 2:
            continue

        degree = clean_degree(parts[0])
        institution_text = YEAR_RANGE_PATTERN.sub("", parts[1])
        institution = clean_institution(
            institution_text.strip(" ,-|–—")
        )

        if not degree or not institution:
            continue

        entries.append(
            build_entry(
                degree=degree,
                institution=institution,
                start_year=start_year,
                end_year=end_year,
                confidence="high"
            )
        )

    return entries


def extract_education_entries(
    education_text: str
) -> list[dict]:
    if not education_text:
        return []

    lines = [
        clean_line(line)
        for line in education_text.splitlines()
        if clean_line(line)
    ]

    # Strategy 1: Extract complete entries from a single line.
    single_line_entries = extract_single_line_education_entries(lines)

    # Strategy 2: Extract entries containing year ranges on separate lines.
    year_entries = extract_year_based_entries(lines)

    # Strategy 3: Extract degree blocks.
    block_entries = extract_degree_block_entries(lines)

    entries = single_line_entries + year_entries + block_entries

    entries = remove_duplicate_entries(entries)

    # Remove likely false-positive entries: a descriptive sentence
    # is not a qualification unless it resembles a degree heading.
    filtered_entries = []

    for entry in entries:
        degree = (entry.get("degree") or "").strip()
        institution = (entry.get("institution") or "").strip()

        if not degree:
            continue

        # Reject sentence-like entries that were mistaken for degrees.
        if (
            len(degree.split()) > 8
            or degree.lower().startswith(
                ("i'm currently", "i’m currently", "currently doing")
            )
        ):
            continue

        filtered_entries.append(entry)

    return filtered_entries