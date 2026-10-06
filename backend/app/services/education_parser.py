import re


YEAR_RANGE_PATTERN = re.compile(
    r"\b(19|20)\d{2}\s*(?:-|–|—|to)\s*(19|20)\d{2}\b",
    re.IGNORECASE
)

SINGLE_YEAR_PATTERN = re.compile(
    r"\b(19|20)\d{2}\b"
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
    "degree"
]


def clean_line(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text.strip()
    )


def extract_year_range(text: str):
    match = YEAR_RANGE_PATTERN.search(text)

    if not match:
        return None, None

    years = re.findall(
        r"\b(?:19|20)\d{2}\b",
        match.group(0)
    )

    if len(years) >= 2:
        return int(years[0]), int(years[1])

    return None, None


def looks_like_degree(text: str) -> bool:

    text_lower = text.lower()

    return any(
        keyword in text_lower
        for keyword in DEGREE_KEYWORDS
    )


def looks_like_institution(text: str) -> bool:

    text_lower = text.lower()

    institution_keywords = [
        "university",
        "college",
        "institute",
        "school",
        "academy",
        "iit",
        "nit"
    ]

    return any(
        keyword in text_lower
        for keyword in institution_keywords
    )


def extract_education_entries(
    education_text: str
) -> list[dict]:

    lines = [
        clean_line(line)
        for line in education_text.splitlines()
        if clean_line(line)
    ]

    entries = []

    i = 0

    while i < len(lines):

        line = lines[i]

        # --------------------------------------------------
        # Pattern:
        #
        # 2024 - 2028
        # Bachelor of Technology Computer Science
        # Rai University
        # Description
        # --------------------------------------------------

        if YEAR_RANGE_PATTERN.search(line):

            start_year, end_year = extract_year_range(
                line
            )

            degree = None
            institution = None
            description_lines = []

            if i + 1 < len(lines):

                possible_degree = lines[i + 1]

                if looks_like_degree(
                    possible_degree
                ):
                    degree = possible_degree

            if i + 2 < len(lines):

                possible_institution = lines[i + 2]

                if (
                    looks_like_institution(
                        possible_institution
                    )
                    or not looks_like_degree(
                        possible_institution
                    )
                ):
                    institution = possible_institution

            start_description = i + 3

            for description_line in lines[
                start_description:
            ]:
                description_lines.append(
                    description_line
                )

            entries.append({
                "degree": degree,
                "institution": institution,
                "start_year": start_year,
                "end_year": end_year,
                "description": " ".join(
                    description_lines
                ),
                "confidence": (
                    "high"
                    if degree and institution
                    else "medium"
                )
            })

            break

        i += 1

    return entries