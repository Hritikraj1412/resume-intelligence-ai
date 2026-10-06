def generate_explanation(
    match_result: dict
) -> dict:

    breakdown = match_result["breakdown"]
    skills = match_result["skills"]
    experience = match_result["experience"]
    projects = match_result["projects"]

    evidence = match_result["evidence_quality"]

    strengths = []
    gaps = []
    warnings = []

    # -----------------------------------------
    # SKILL STRENGTHS
    # -----------------------------------------

    for skill in skills["matched"]:
        strengths.append(
            f"{skill} matches the required job skills."
        )

    # -----------------------------------------
    # MISSING SKILLS
    # -----------------------------------------

    for skill in skills["missing_required"]:
        gaps.append(
            f"{skill} is required by the job but was not detected in the resume."
        )

    # -----------------------------------------
    # EXPERIENCE ANALYSIS
    # -----------------------------------------

    if experience["status"] == "meets_requirement":

        strengths.append(
            f"Detected {experience['resume_years']} years of experience, "
            f"which meets the required {experience['required_years']} years."
        )

    elif experience["status"] == "partially_meets":

        gaps.append(
            f"The job requires approximately "
            f"{experience['required_years']} years of experience, "
            f"while the resume shows about "
            f"{experience['resume_years']} years."
        )

    elif experience["status"] == "no_experience_detected":

        gaps.append(
            "No relevant professional experience was detected."
        )

    # -----------------------------------------
    # PROJECT ANALYSIS
    # -----------------------------------------

    if projects:

        strongest_project = max(
            projects,
            key=lambda project: project["score"]
        )

        strengths.append(
            f"Strongest detected project evidence: "
            f"{strongest_project['project']} "
            f"with a relevance score of "
            f"{strongest_project['score']}%."
        )

        for project in projects:

            if project["score"] < 20:

                warnings.append(
                    f"{project['project']} has relatively low "
                    f"relevance to the job responsibilities."
                )

    # -----------------------------------------
    # SCORE ANALYSIS
    # -----------------------------------------

    if breakdown["skill_match"] >= 70:

        strengths.append(
            "The resume has strong coverage of the required skills."
        )

    elif breakdown["skill_match"] >= 40:

        warnings.append(
            "The resume has moderate coverage of the required skills."
        )

    else:

        gaps.append(
            "The resume has low coverage of the required skills."
        )

    if breakdown["semantic_match"] >= 70:

        strengths.append(
            "Resume content is semantically well aligned with the job description."
        )

    elif breakdown["semantic_match"] < 40:

        warnings.append(
            "The resume content has relatively low semantic similarity "
            "to the job description."
        )

    if breakdown["tfidf_match"] < 30:

        warnings.append(
            "Keyword-based textual similarity is relatively low."
        )

    if breakdown["project_relevance"] < 30:

        warnings.append(
            "Projects show limited relevance to the responsibilities "
            "described in the job."
        )

    if evidence["score"] >= 70:

        strengths.append(
            "The resume provides strong supporting evidence "
            "through relevant skills, experience, and projects."
        )

    elif evidence["score"] >= 40:

        warnings.append(
            "The resume provides moderate supporting evidence "
            "for the skills and responsibilities detected in the job."
        )

    else:

        warnings.append(
            "The resume contains limited supporting evidence "
            "for the requirements of this job."
        )

    if evidence["project_relevance"] >= 70:

        strengths.append(
            "Projects show strong semantic relevance "
            "to the job responsibilities."
        )

    elif (
        projects
        and evidence["project_relevance"] < 40
    ):

        warnings.append(
            "The listed projects have relatively limited "
            "semantic relevance to the job responsibilities."
        )

    return {
        "strengths": strengths,
        "gaps": gaps,
        "warnings": warnings
    }