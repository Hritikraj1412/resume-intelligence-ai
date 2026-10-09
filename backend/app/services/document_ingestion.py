import io
import re
from pathlib import Path

import pymupdf
import pytesseract

from PIL import Image, ImageOps, ImageFilter
from docx import Document

from app.services.pdf_parser import extract_text_from_pdf


# =========================================================
# CONFIGURATION
# =========================================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/jpeg",
    "image/png",
    "image/webp",
}

OCR_DPI = 300


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_document_text(text: str) -> str:
    """
    Normalize extracted document text while preserving
    useful resume structure.
    """

    if not text:
        return ""

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\x00", "")

    # Normalize spaces but keep line breaks
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove spaces around line breaks
    text = re.sub(r" *\n *", "\n", text)

    return text.strip()


# =========================================================
# QUALITY ESTIMATION
# =========================================================

def calculate_extraction_quality(text: str) -> int:
    """
    Heuristic extraction quality score.

    This is NOT an AI accuracy probability.
    It estimates whether the extracted text looks usable.
    """

    if not text:
        return 0

    score = 0

    character_count = len(text)

    words = re.findall(
        r"\b[A-Za-z]{2,}\b",
        text
    )

    alphanumeric = re.findall(
        r"[A-Za-z0-9]",
        text
    )

    # -----------------------------------------------------
    # Character quantity
    # -----------------------------------------------------

    if character_count >= 2500:
        score += 35
    elif character_count >= 1500:
        score += 30
    elif character_count >= 800:
        score += 22
    elif character_count >= 300:
        score += 15
    elif character_count >= 100:
        score += 8

    # -----------------------------------------------------
    # Word quantity
    # -----------------------------------------------------

    if len(words) >= 300:
        score += 25
    elif len(words) >= 180:
        score += 20
    elif len(words) >= 100:
        score += 15
    elif len(words) >= 50:
        score += 10
    elif len(words) >= 20:
        score += 5

    # -----------------------------------------------------
    # Alphanumeric content
    # -----------------------------------------------------

    if len(alphanumeric) >= 1000:
        score += 20
    elif len(alphanumeric) >= 500:
        score += 15
    elif len(alphanumeric) >= 200:
        score += 10
    elif len(alphanumeric) >= 80:
        score += 5

    # -----------------------------------------------------
    # Resume structure indicators
    # -----------------------------------------------------

    resume_keywords = [
        "experience",
        "education",
        "skills",
        "projects",
        "summary",
        "profile",
        "certification",
        "contact",
        "objective",
    ]

    lowered = text.lower()

    detected_sections = sum(
        1
        for keyword in resume_keywords
        if keyword in lowered
    )

    score += min(
        detected_sections * 4,
        20
    )

    return min(score, 100)


# =========================================================
# IMAGE PREPROCESSING
# =========================================================

def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Prepare an image for OCR.
    """

    # Convert to RGB
    image = image.convert("RGB")

    # Convert to grayscale
    image = ImageOps.grayscale(image)

    # Increase contrast
    image = ImageOps.autocontrast(image)

    # Light denoising
    image = image.filter(
        ImageFilter.MedianFilter(size=3)
    )

    return image


# =========================================================
# IMAGE OCR
# =========================================================

def extract_text_from_image(
    file_bytes: bytes
) -> str:
    """
    Extract text from JPG, JPEG, PNG or WEBP
    using Tesseract OCR.
    """

    try:

        image = Image.open(
            io.BytesIO(file_bytes)
        )

    except Exception as exc:

        raise ValueError(
            f"Unable to open image: {exc}"
        ) from exc

    image = preprocess_image(image)

    try:

        text = pytesseract.image_to_string(
            image,
            config="--psm 3"
        )

    except Exception as exc:

        raise RuntimeError(
            f"Image OCR failed: {exc}"
        ) from exc

    return clean_document_text(text)


# =========================================================
# DOCX EXTRACTION
# =========================================================

def extract_text_from_docx(
    file_bytes: bytes
) -> str:
    """
    Extract text from DOCX resumes.

    Reads:
        - paragraphs
        - table cells
    """

    try:

        document = Document(
            io.BytesIO(file_bytes)
        )

    except Exception as exc:

        raise ValueError(
            f"Unable to open DOCX file: {exc}"
        ) from exc

    parts = []

    # -----------------------------------------------------
    # Paragraphs
    # -----------------------------------------------------

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            parts.append(text)

    # -----------------------------------------------------
    # Tables
    # -----------------------------------------------------

    for table in document.tables:

        for row in table.rows:

            cells = []

            for cell in row.cells:

                text = cell.text.strip()

                if text:
                    cells.append(text)

            if cells:
                parts.append(
                    " | ".join(cells)
                )

    return clean_document_text(
        "\n".join(parts)
    )


# =========================================================
# PDF METADATA
# =========================================================

def get_pdf_page_count(
    file_bytes: bytes
) -> int:

    try:

        document = pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        )

        page_count = len(document)

        document.close()

        return page_count

    except Exception:

        return 0


# =========================================================
# UNIVERSAL DOCUMENT INGESTION
# =========================================================

def ingest_document(
    file_bytes: bytes,
    filename: str,
    content_type: str | None = None
) -> dict:
    """
    Universal resume document ingestion.

    Supported:
        PDF
        DOCX
        JPG
        JPEG
        PNG
        WEBP
    """

    if not file_bytes:

        raise ValueError(
            "Uploaded file is empty."
        )

    if not filename:

        raise ValueError(
            "Uploaded file has no filename."
        )

    extension = Path(
        filename
    ).suffix.lower()

    # -----------------------------------------------------
    # Validate extension
    # -----------------------------------------------------

    if extension not in SUPPORTED_EXTENSIONS:

        raise ValueError(
            "Unsupported resume format. "
            "Supported formats: PDF, DOCX, JPG, JPEG, PNG and WEBP."
        )

    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    if extension == ".pdf":

        text = extract_text_from_pdf(
            file_bytes
        )

        text = clean_document_text(
            text
        )

        if not text:

            raise ValueError(
                "Could not extract readable text from the PDF."
            )

        page_count = get_pdf_page_count(
            file_bytes
        )

        # Existing PDF parser automatically decides
        # between normal extraction and OCR.
        extraction_method = "pdf_text_or_ocr"

        return {
            "text": text,
            "filename": filename,
            "file_type": "pdf",
            "content_type": content_type,
            "extraction_method": extraction_method,
            "ocr_used": False,
            "pages": page_count,
            "character_count": len(text),
            "extraction_quality": calculate_extraction_quality(text),
        }

    # -----------------------------------------------------
    # DOCX
    # -----------------------------------------------------

    if extension == ".docx":

        text = extract_text_from_docx(
            file_bytes
        )

        if not text:

            raise ValueError(
                "Could not extract readable text from the DOCX file."
            )

        return {
            "text": text,
            "filename": filename,
            "file_type": "docx",
            "content_type": content_type,
            "extraction_method": "docx",
            "ocr_used": False,
            "pages": None,
            "character_count": len(text),
            "extraction_quality": calculate_extraction_quality(text),
        }

    # -----------------------------------------------------
    # IMAGE
    # -----------------------------------------------------

    if extension in {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }:

        text = extract_text_from_image(
            file_bytes
        )

        if not text:

            raise ValueError(
                "Could not detect readable text in the uploaded image."
            )

        return {
            "text": text,
            "filename": filename,
            "file_type": "image",
            "content_type": content_type,
            "extraction_method": "ocr",
            "ocr_used": True,
            "pages": 1,
            "character_count": len(text),
            "extraction_quality": calculate_extraction_quality(text),
        }

    # -----------------------------------------------------
    # Safety fallback
    # -----------------------------------------------------

    raise ValueError(
        "Unsupported document format."
    )