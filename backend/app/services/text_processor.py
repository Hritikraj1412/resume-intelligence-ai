import re


def clean_text(text: str) -> str:
    # Remove extra spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n+", "\n", text)

    # Remove leading and trailing whitespace
    text = text.strip()

    return text