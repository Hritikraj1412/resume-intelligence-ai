def generate_recommendations(
    match_result: dict,
    job_analysis: dict
) -> list[dict]:

    recommendations = []

    skills = match_result["skills"]
    experience = match_result["experience"]
    projects = match_result["projects"]
    breakdown = match_result["breakdown"]

    # =========================================
    # MISSING REQUIRED SKILLS
    # =========================================

    for skill in skills["missing_required"]:

        recommendations.append({
            "type": "skill_gap",
            "priority": "high",
            "title": f"Address the {skill} skill gap",
            "recommendation": (
                f"If you genuinely have experience with {skill}, "
                f"make that experience more visible in your resume. "
                f"If you do not have the skill, consider learning it "
                f"and building a relevant project."
            )
        })

    # =========================================
    # EXPERIENCE GAP
    # =========================================

    if experience["status"] == "partially_meets":

        recommendations.append({
            "type": "experience_gap",
            "priority": "high",
            "title": "Strengthen experience evidence",
            "recommendation": (
                f"The job asks for approximately "
                f"{experience['required_years']} years of experience, "
                f"while the resume currently shows about "
                f"{experience['resume_years']} years. "
                f"Highlight relevant internships, freelance work, "
                f"open-source contributions, and substantial projects "
                f"if they genuinely apply."
            )
        })

    elif experience["status"] == "no_experience_detected":

        recommendations.append({
            "type": "experience_gap",
            "priority": "high",
            "title": "Add relevant experience evidence",
            "recommendation": (
                "No professional experience was detected. "
                "If you have internships, freelance work, "
                "open-source contributions, or other relevant "
                "experience, make sure they are clearly listed."
            )
        })

    # =========================================
    # PROJECT RECOMMENDATION
    # =========================================

    if projects:

        strongest_project = max(
            projects,
            key=lambda project: project["score"]
        )

        recommendations.append({
            "type": "project",
            "priority": "medium",
            "title": "Highlight your strongest relevant project",
            "recommendation": (
                f"Consider giving more visibility to "
                f"'{strongest_project['project']}', "
                f"because it currently has the highest detected "
                f"relevance score of "
                f"{strongest_project['score']}%."
            )
        })

    else:

        recommendations.append({
            "type": "project",
            "priority": "medium",
            "title": "Add relevant projects",
            "recommendation": (
                "Consider adding projects that demonstrate "
                "skills and responsibilities relevant to this job."
            )
        })

    # =========================================
    # TF-IDF / KEYWORD ALIGNMENT
    # =========================================

    if breakdown["tfidf_match"] < 30:

        recommendations.append({
            "type": "keyword_alignment",
            "priority": "medium",
            "title": "Improve keyword alignment",
            "recommendation": (
                "The resume has relatively low keyword similarity "
                "to the job description. Where truthful, use the "
                "same technical terminology used in the job description "
                "when describing your actual skills and experience."
            )
        })

    # =========================================
    # SEMANTIC ALIGNMENT
    # =========================================

    if breakdown["semantic_match"] < 50:

        recommendations.append({
            "type": "content_alignment",
            "priority": "medium",
            "title": "Improve content alignment",
            "recommendation": (
                "The resume content has relatively low semantic "
                "alignment with the job description. Consider "
                "rewriting relevant project and experience descriptions "
                "to clearly explain responsibilities and outcomes "
                "that genuinely relate to this role."
            )
        })

    # =========================================
    # PROJECT RELEVANCE
    # =========================================

    if breakdown["project_relevance"] < 30:

        recommendations.append({
            "type": "project_relevance",
            "priority": "medium",
            "title": "Increase project relevance",
            "recommendation": (
                "Your projects currently show limited relevance "
                "to the job responsibilities. If applicable, "
                "highlight projects involving the technologies, "
                "APIs, databases, architecture, or responsibilities "
                "mentioned in the job description."
            )
        })

    return recommendations