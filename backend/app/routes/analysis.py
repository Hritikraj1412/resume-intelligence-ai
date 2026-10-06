from fastapi import APIRouter
from pydantic import BaseModel

from app.services.skill_extractor import extract_skills
from app.services.job_description_parser import parse_job_description
from app.services.match_engine import calculate_final_match
from app.services.explanation_engine import generate_explanation
from app.services.recommendation_engine import generate_recommendations
from app.services.experience_parser import extract_experience_entries
from app.services.project_parser import extract_project_entries
from app.services.resume_section_parser import extract_resume_sections


router = APIRouter(
    prefix="/api/analysis",
    tags=["Analysis"]
)


class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    job_description: str


@router.post("/match")
def match_resume(data: ResumeAnalysisRequest):

    # =========================================
    # 1. RESUME PROCESSING
    # =========================================

    resume_sections = extract_resume_sections(
        data.resume_text
    )

    resume_skills = extract_skills(
        data.resume_text
    )

    resume_experience = extract_experience_entries(
        resume_sections.get("experience", "")
    )

    print("DEBUG EXPERIENCE:", resume_experience)

    resume_projects = extract_project_entries(
        resume_sections.get("projects", "")
    )

    # =========================================
    # 2. JOB DESCRIPTION PROCESSING
    # =========================================

    job_data = parse_job_description(
        data.job_description
    )

    # =========================================
    # 3. MATCH ENGINE
    # =========================================

    match_result = calculate_final_match(
        resume_text=data.resume_text,
        job_description=data.job_description,
        resume_skills=resume_skills,
        required_skills=job_data["required_skills"],
        preferred_skills=job_data["preferred_skills"],
        resume_experience=resume_experience,
        required_experience=job_data["experience_required"],
        resume_projects=resume_projects,
        responsibilities=job_data["responsibilities"]
    )

    # =========================================
    # 4. EXPLAINABLE AI
    # =========================================

    explanation = generate_explanation(
        match_result
    )

    # =========================================
    # 5. AI RECOMMENDATIONS
    # =========================================

    recommendations = generate_recommendations(
        match_result=match_result,
        job_analysis=job_data
    )

    # =========================================
    # 6. FINAL RESPONSE
    # =========================================

    return {
        **match_result,
        "job_analysis": job_data,
        "explanation": explanation,
        "recommendations": recommendations
    }