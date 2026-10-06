import json
import re
from pathlib import Path


# --------------------------------------------------
# Load skill taxonomy
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[3]

SKILLS_FILE = BASE_DIR / "data" / "skills.json"


with open(
    SKILLS_FILE,
    "r",
    encoding="utf-8"
) as file:

    SKILL_TAXONOMY = json.load(file)


# --------------------------------------------------
# Build alias -> canonical skill mapping
# --------------------------------------------------

SKILL_ALIASES = {}

for category in SKILL_TAXONOMY.values():

    for canonical_skill, aliases in category.items():

        for alias in aliases:

            SKILL_ALIASES[
                alias.lower()
            ] = canonical_skill


# --------------------------------------------------
# Normalize text
# --------------------------------------------------

def normalize_text(text: str) -> str:

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# --------------------------------------------------
# Check whether an alias exists as a
# complete word/phrase
# --------------------------------------------------

def contains_skill(
    text: str,
    skill: str
) -> bool:

    escaped_skill = re.escape(skill)

    pattern = rf"(?<![a-z0-9+#]){escaped_skill}(?![a-z0-9+#])"

    return bool(
        re.search(
            pattern,
            text,
            re.IGNORECASE
        )
    )


# --------------------------------------------------
# Extract normalized skills
# --------------------------------------------------

def extract_skills(text: str) -> list[str]:

    normalized_text = normalize_text(text)

    found_skills = set()

    for alias, canonical_skill in SKILL_ALIASES.items():

        if contains_skill(
            normalized_text,
            alias
        ):

            found_skills.add(
                canonical_skill
            )

    return sorted(found_skills)