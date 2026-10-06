from app.routes.analysis import router as analysis_router
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.contact_parser import extract_contact_information
from app.services.pdf_parser import extract_text_from_pdf
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

# CORS - allows React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
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

    # --------------------------------------------------
    # 1. Validate file
    # --------------------------------------------------

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    # --------------------------------------------------
    # 2. Read PDF
    # --------------------------------------------------

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
      raise HTTPException(
        status_code=413,
        detail="PDF file is too large. Maximum allowed size is 5 MB."
    )

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded PDF is empty."
        )

    try:

        # --------------------------------------------------
        # 3. Extract text
        # --------------------------------------------------

        text = extract_text_from_pdf(file_bytes)

        text = clean_text(text)

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from this PDF."
            )

        # --------------------------------------------------
        # 4. Extract resume sections
        # --------------------------------------------------

        sections = extract_resume_sections(text)

        # --------------------------------------------------
        # 5. Extract skills
        # --------------------------------------------------

        skills = extract_skills(text)

        # --------------------------------------------------
        # 6. Extract structured experience
        # --------------------------------------------------

        experience = extract_experience_entries(
            sections["experience"]
        )

        contact = extract_contact_information(text)

        education = extract_education_entries(
             sections["education"]
       )
         
        projects = extract_project_entries(
             sections["projects"]
       )

        # --------------------------------------------------
        # 7. Return structured resume data
        # --------------------------------------------------

        return {
            "filename": file.filename,

            "metadata": {
                "characters": len(text)
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

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Resume processing failed: {str(error)}"
        )