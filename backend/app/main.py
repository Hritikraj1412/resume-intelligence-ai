from app.routes.analysis import router as analysis_router
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.contact_parser import extract_contact_information
from app.services.document_ingestion import ingest_document
from app.services.text_processor import clean_text
from app.services.skill_extractor import extract_skills
from app.services.resume_section_parser import extract_resume_sections
from app.services.experience_parser import extract_experience_entries
from app.services.education_parser import extract_education_entries
from app.services.project_parser import extract_project_entries
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


app = FastAPI(
    title="Resume Intelligence AI",
    description="AI-powered resume analysis and job matching system",
    version="1.0.0"
)

app.include_router(analysis_router)


import os

# CORS - local development and deployed frontend
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

frontend_url = os.getenv("FRONTEND_URL", "").strip().rstrip("/")

if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Invalid request data.",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):
    print(
        f"Unhandled error: {type(exc).__name__}: {exc}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected server error occurred."
        }
    )


@app.get("/")
def root():
    return {
        "message": "Resume Intelligence AI API is running",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

MAX_FILE_SIZE = 5 * 1024 * 1024

@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):

    # ==================================================
    # 1. VALIDATE FILE
    # ==================================================

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided."
        )

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    }

    extension = (
        "." + file.filename.split(".")[-1].lower()
        if "." in file.filename
        else ""
    )

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported resume format. "
                "Supported formats: PDF, DOCX, JPG, JPEG, PNG and WEBP."
            )
        )

    # ==================================================
    # 2. READ FILE
    # ==================================================

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # ==================================================
    # 3. FILE SIZE LIMIT
    # ==================================================

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Resume file is too large. Maximum allowed size is 5 MB."
        )

    # ==================================================
    # 4. UNIVERSAL DOCUMENT INGESTION
    # ==================================================

    try:

        document = ingest_document(
            file_bytes=file_bytes,
            filename=file.filename,
            content_type=file.content_type
        )

        text = document["text"]

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract readable text from this resume."
            )

        # ==================================================
        # 5. EXTRACT RESUME SECTIONS
        # ==================================================

        sections = extract_resume_sections(text)

        # ==================================================
        # 6. EXTRACT SKILLS
        # ==================================================

        skills = extract_skills(text)

        # ==================================================
        # 7. EXTRACT EXPERIENCE
        # ==================================================

        experience = extract_experience_entries(
            sections.get("experience", "")
        )

        # ==================================================
        # 8. EXTRACT CONTACT
        # ==================================================

        contact = extract_contact_information(text)

        # ==================================================
        # 9. EXTRACT EDUCATION
        # ==================================================

        education = extract_education_entries(
            sections.get("education", "")
        )

        # ==================================================
        # 10. EXTRACT PROJECTS
        # ==================================================

        projects = extract_project_entries(
            sections.get("projects", "")
        )

        # ==================================================
        # 11. RETURN STRUCTURED RESUME DATA
        # ==================================================

        return {
            "filename": file.filename,

            "metadata": {
                "file_type": document["file_type"],
                "content_type": document["content_type"],
                "extraction_method": document["extraction_method"],
                "ocr_used": document["ocr_used"],
                "pages": document["pages"],
                "characters": document["character_count"],
                "extraction_quality": document["extraction_quality"]
            },

            "contact": contact,

            "education": education,

            "projects": projects,

            "text": text,

            "skills": skills,

            "sections": sections,

            "experience": experience
        }

    except HTTPException:
        raise

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(
            f"Resume processing error: "
            f"{type(error).__name__}: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Resume processing failed."
        )