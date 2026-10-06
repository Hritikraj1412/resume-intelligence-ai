import re

from app.services.skill_extractor import extract_skills


def clean_line(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        text.strip()
    )


def parse_project_line(line: str) -> dict:

    line = clean_line(line)

    if not line:
        return {
            "name": None,
            "description": "",
            "technologies": [],
            "confidence": "low"
        }

    # --------------------------------------------------
    # Split project name and description
    #
    # Example:
    #
    # Expense Tracker Web App :
    # Built using React.js and Node.js
    # --------------------------------------------------

    parts = re.split(
        r"\s*:\s*",
        line,
        maxsplit=1
    )

    if len(parts) == 2:

        name = parts[0].strip()
        description = parts[1].strip()

    else:

        name = line
        description = ""

    # --------------------------------------------------
    # Detect technologies from the complete line
    # --------------------------------------------------

    technologies = extract_skills(line)

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------

    if name and description and technologies:

        confidence = "high"

    elif name and (
        description or technologies
    ):

        confidence = "medium"

    else:

        confidence = "low"

    return {
        "name": name,
        "description": description,
        "technologies": technologies,
        "confidence": confidence
    }


def extract_project_entries(
    projects_text: str
) -> list[dict]:

    lines = [
        clean_line(line)
        for line in projects_text.splitlines()
        if clean_line(line)
    ]

    entries = []

    for line in lines:

        project = parse_project_line(line)

        if project["name"]:

            entries.append(project)

    return entries