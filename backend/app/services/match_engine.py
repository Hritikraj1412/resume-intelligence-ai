from app.services.tfidf_matcher import calculate_tfidf_similarity
from app.services.semantic_matcher import calculate_semantic_similarity
from app.services.skill_matcher import calculate_skill_match
from app.services.experience_matcher import calculate_experience_match
from app.services.project_matcher import calculate_project_relevance
from app.services.match_classifier import classify_match
from app.services.evidence_quality import calculate_evidence_quality


def calculate_final_match(
    resume_text: str,
    job_description: str,
    resume_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str],
    resume_experience: list[dict],
    required_experience: str | None,
    resume_projects: list[dict],
    responsibilities: list[str]
) -> dict:

    # --------------------------------
    # 1. REQUIRED SKILL MATCH
    # --------------------------------

    skill_result = calculate_skill_match(
    resume_skills=resume_skills,
    required_skills=required_skills,
    preferred_skills=preferred_skills
)

    # --------------------------------
    # 2. TF-IDF MATCH
    # --------------------------------

    tfidf_score = calculate_tfidf_similarity(
        resume_text,
        job_description
    )

    # --------------------------------
    # 3. SEMANTIC MATCH
    # --------------------------------

    semantic_score = calculate_semantic_similarity(
        resume_text,
        job_description
    )

    # --------------------------------
    # 4. EXPERIENCE MATCH
    # --------------------------------

    experience_result = calculate_experience_match(
        resume_experience,
        required_experience
    )

    # --------------------------------
    # 5. PROJECT RELEVANCE
    # --------------------------------

    project_result = calculate_project_relevance(
        resume_projects,
        required_skills,
        responsibilities
    )

    evidence_result = calculate_evidence_quality(
    resume_experience=resume_experience,
    resume_projects=resume_projects,
    resume_skills=resume_skills,
    required_skills=required_skills,
    responsibilities=responsibilities
)

    # -------------------------------------------------
    # DYNAMIC EVIDENCE-AWARE SCORING
    # -------------------------------------------------

    score_components = {
        "skill_match": (
            skill_result["score"],
            0.25
        ),
        "semantic_match": (
            semantic_score,
            0.25
        ),
        "tfidf_match": (
            tfidf_score,
            0.10
        )
    }

    if experience_result["score"] is not None:
     score_components["experience_match"] = (
        experience_result["score"],
        0.15
    )

    # Project relevance is only included when
    # actual projects are available.
    if resume_projects:
        score_components["project_relevance"] = (
            project_result["score"],
            0.25
        )

    total_weight = sum(
        weight
        for _, weight in score_components.values()
    )
    
    scoring_metadata = {
        "included_components": list(score_components.keys()),
        "component_weights": {
            name: weight
            for name, (_, weight) in score_components.items()
        },
        "total_weight_before_normalization": round(total_weight, 4),
        "weights_normalized": total_weight > 0 and total_weight != 1.0,
    }

    content_alignment = (
    (semantic_score * 0.70)
    + (tfidf_score * 0.30)
)

    content_alignment = round(
    content_alignment,
    2
)         

    final_score = sum(
        score * weight
        for score, weight in score_components.values()
    )

    # Normalize the score when some evidence
    # categories are unavailable.
    if total_weight > 0:
        final_score = final_score / total_weight

    final_score = round(
        min(max(final_score, 0.0), 100.0),
        2
    )

    classification = classify_match(
    match_score=final_score,
    skill_coverage=skill_result["coverage"],
    content_alignment=content_alignment
)

    return {
        "match_score": final_score,
        "scoring_metadata": scoring_metadata,
        "classification": classification,
             "match_quality": {
    "skill_coverage": skill_result["coverage"],
    "required_skill_coverage": skill_result[
        "required_coverage"
    ],
    "preferred_skill_coverage": skill_result[
        "preferred_coverage"
    ],
    "content_alignment": content_alignment
},
        
        "breakdown": {
            "skill_match": skill_result["score"],
            "semantic_match": semantic_score,
            "tfidf_match": tfidf_score,
            "experience_match": experience_result["score"],
            "project_relevance": project_result["score"]
        },

        "skills": {
    "matched": skill_result["matched"],
    "missing_required": skill_result["missing"],

    "preferred": preferred_skills,

    "preferred_matched": skill_result[
        "preferred_matched"
    ],

    "preferred_missing": skill_result[
        "preferred_missing"
    ],

    "required_coverage": skill_result[
        "required_coverage"
    ],

    "preferred_coverage": skill_result[
        "preferred_coverage"
    ]
},

        "experience": experience_result,

        "projects": project_result["projects"],

        "evidence_quality": evidence_result,
    }
