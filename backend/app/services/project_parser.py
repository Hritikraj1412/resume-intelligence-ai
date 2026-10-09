
import re

from app.services.skill_extractor import extract_skills


def clean_line(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def parse_project_line(line: str) -> dict:
    line = clean_line(line)

    if not line:
        return {
            "name": None,
            "description": "",
            "technologies": [],
            "confidence": "low",
        }

    # Split project name from the remaining content.
    # Supports: "Project: description" and "Project — description".
    parts = re.split(r"\s*:\s*|\s+[—–]\s+", line, maxsplit=1)

    if len(parts) == 2:
        name = parts[0].strip()
        remainder = parts[1].strip()
    else:
        name = line
        remainder = ""

    # Extract technologies from the entire original line.
    technologies = extract_skills(line)

    # Remove an initial technology list from the description.
    description = remainder

    if description:
        description = re.sub(
            r"^[,;:\s]*(?:built\s+using|using|built\s+with)\s+",
            "",
            description,
            flags=re.IGNORECASE,
        ).strip()

        # If the remainder starts with a technology list,
        # keep the descriptive text after the first semicolon.
        if ";" in description:
            first, rest = description.split(";", 1)
            if extract_skills(first):
                description = rest.strip()

    # Avoid returning a technology list as the project description.
    description = description.strip(" ;,") if description else ""

    if name and description and technologies:
        confidence = "high"
    elif name and (description or technologies):
        confidence = "medium"
    else:
        confidence = "low"

    return {
        "name": name,
        "description": description,
        "technologies": technologies,
        "confidence": confidence,
    }


def extract_project_entries(projects_text: str) -> list[dict]:
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