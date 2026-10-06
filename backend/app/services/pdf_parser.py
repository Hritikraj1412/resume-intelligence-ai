import io
import re

import pymupdf
import pytesseract

from PIL import Image


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# =========================================================
# CONFIG
# =========================================================

MIN_TEXT_LENGTH = 80
MIN_TEXT_PER_PAGE = 25


# =========================================================
# TEXT CLEANING
# =========================================================

def clean_extracted_text(text: str) -> str:
    """
    Clean extracted PDF/OCR text while preserving
    useful resume structure.
    """

    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove null characters
    text = text.replace("\x00", "")

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove repeated whitespace around newlines
    text = re.sub(r" *\n *", "\n", text)

    return text.strip()


# =========================================================
# TEXT EXTRACTION
# =========================================================

def extract_text_layer(document) -> str:
    """
    Extract normal text from a PDF using PyMuPDF.
    Uses block positioning to preserve layout better.
    """

    pages = []

    for page in document:

        blocks = page.get_text(
            "blocks",
            sort=True
        )

        page_blocks = []

        for block in blocks:

            if len(block) < 5:
                continue

            x0, y0, x1, y1, text = block[:5]

            text = text.strip()

            if not text:
                continue

            page_blocks.append(
                {
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1,
                    "text": text
                }
            )

        # Sort top → bottom, then left → right
        page_blocks.sort(
            key=lambda item: (
                round(item["y0"] / 8),
                item["x0"]
            )
        )

        page_text = []

        for block in page_blocks:
            page_text.append(
                block["text"]
            )

        if page_text:
            pages.append(
                "\n".join(page_text)
            )

    return "\n\n".join(pages)


# =========================================================
# TEXT QUALITY CHECK
# =========================================================

def is_text_usable(
    text: str,
    page_count: int
) -> bool:
    """
    Determine whether normal PDF extraction produced
    enough useful content.
    """

    if not text:
        return False

    cleaned = clean_extracted_text(text)

    if len(cleaned) < MIN_TEXT_LENGTH:
        return False

    # Count meaningful alphanumeric characters
    alphanumeric = len(
        re.findall(
            r"[A-Za-z0-9]",
            cleaned
        )
    )

    if alphanumeric < 50:
        return False

    # Avoid accepting garbage extraction
    words = re.findall(
        r"\b[A-Za-z]{2,}\b",
        cleaned
    )

    if len(words) < 10:
        return False

    return True


# =========================================================
# IMAGE / OCR FALLBACK
# =========================================================

def extract_text_with_ocr(document) -> str:
    """
    OCR fallback for scanned/image-based PDFs.

    Requires:
        pytesseract
        Pillow
    """

    try:

        import pytesseract
        from PIL import Image

    except ImportError as exc:

        raise RuntimeError(
            "OCR dependencies are missing. "
            "Install pytesseract and Pillow."
        ) from exc


    pages = []


    for page_number, page in enumerate(document):

        # Render page at high enough resolution for OCR
        matrix = pymupdf.Matrix(
            2.0,
            2.0
        )

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        image_bytes = pixmap.tobytes(
            "png"
        )

        image = Image.open(
            io.BytesIO(image_bytes)
        )


        try:

            text = pytesseract.image_to_string(
                image,
                config="--psm 3"
            )

        except Exception as exc:

            raise RuntimeError(
                f"OCR failed on page "
                f"{page_number + 1}: {exc}"
            ) from exc


        text = clean_extracted_text(
            text
        )

        if text:
            pages.append(text)


    return "\n\n".join(pages)


# =========================================================
# MAIN EXTRACTION
# =========================================================

def extract_text_from_pdf(
    file_bytes: bytes
) -> str:

    if not file_bytes:
        raise ValueError(
            "The uploaded PDF is empty."
        )


    try:

        document = pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        )

    except Exception as exc:

        raise ValueError(
            f"Unable to open PDF: {exc}"
        ) from exc


    try:

        page_count = len(document)

        if page_count == 0:

            raise ValueError(
                "The PDF contains no pages."
            )


        # =================================================
        # METHOD 1 — NORMAL TEXT EXTRACTION
        # =================================================

        extracted_text = extract_text_layer(
            document
        )

        extracted_text = clean_extracted_text(
            extracted_text
        )


        if is_text_usable(
            extracted_text,
            page_count
        ):

            return extracted_text


        # =================================================
        # METHOD 2 — OCR FALLBACK
        # =================================================

        print(
            "Normal PDF text extraction produced "
            "insufficient text. Starting OCR..."
        )


        ocr_text = extract_text_with_ocr(
            document
        )

        ocr_text = clean_extracted_text(
            ocr_text
        )


        if not ocr_text:

            raise ValueError(
                "Could not extract text from this PDF. "
                "The document may contain an unsupported "
                "format or unreadable images."
            )


        return ocr_text


    finally:

        document.close()