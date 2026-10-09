from sklearn.metrics.pairwise import cosine_similarity

from app.services.embedding_model import get_embedding_model
from app.services.skill_extractor import extract_skills


def calculate_text_relevance(
    evidence_text: str,
    responsibilities: list[str]
) -> float:

    if not evidence_text.strip():
        return 0.0

    if not responsibilities:
        return 0.0

    responsibility_text = " ".join(
        responsibilities
    ).strip()

    model = get_embedding_model()

    embeddings = model.encode([
        evidence_text,
        responsibility_text
    ])

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    similarity = max(
        0.0,
        min(1.0, float(similarity))
    )

    return round(
        similarity * 100,
        2
    )


def calculate_evidence_quality(
    resume_experience: list[dict],
    resume_projects: list[dict],
    resume_skills: list[str],
    required_skills: list[str],
    responsibilities: list[str]
) -> dict:

   
    # --------------------------------------------------
    # 1. Skill evidence
    # --------------------------------------------------

    required_set = {
        skill.strip().lower()
        for skill in required_skills
        if skill and skill.strip()
    }

    resume_set = {
        skill.strip().lower()
        for skill in resume_skills
        if skill and skill.strip()
    }

    # Keep skill evidence consistent with skill_matcher.py.
    compatibility = {
        "sql": {"sql", "mysql", "postgresql"},
    }

    matched_skills = []

    for required_skill in sorted(required_set):
        acceptable_skills = compatibility.get(
            required_skill,
            {required_skill}
        )

        if resume_set.intersection(acceptable_skills):
            matched_skills.append(required_skill)

    skill_coverage = (
        len(matched_skills) / len(required_set) * 100
        if required_set
        else 0.0
    )
    
    # --------------------------------------------------
    # 2. Experience relevance
    # --------------------------------------------------

    experience_scores = []

    for experience in resume_experience:

        job_title = experience.get(
            "job_title",
            ""
        )

        company = experience.get(
            "company",
            ""
        )

        description = experience.get(
            "description",
            ""
        )

        experience_text = (
            f"{job_title}. "
            f"{company}. "
            f"{description}"
        ).strip()

        score = calculate_text_relevance(
            experience_text,
            responsibilities
        )

        experience_scores.append(
            score
        )

    if experience_scores:

        experience_relevance = (
            sum(experience_scores)
            / len(experience_scores)
        )

    else:

        experience_relevance = 0.0

    # --------------------------------------------------
    # 3. Project relevance
    # --------------------------------------------------

    project_scores = []

    project_skill_scores = []

    for project in resume_projects:

        project_name = project.get(
            "name",
            ""
        )

        project_description = project.get(
            "description",
            ""
        )

        project_text = (
            f"{project_name}. "
            f"{project_description}"
        ).strip()

        relevance = calculate_text_relevance(
            project_text,
            responsibilities
        )

        project_scores.append(
            relevance
        )

        project_skills = set(
            skill.lower()
            for skill in extract_skills(
                project_text
            )
        )

        if required_set:

            matched_project_skills = (
                project_skills.intersection(
                    required_set
                )
            )

            project_skill_score = (
                len(matched_project_skills)
                / len(required_set)
            ) * 100

        else:

            project_skill_score = 0.0

        project_skill_scores.append(
            project_skill_score
        )

    if project_scores:

        project_relevance = (
            sum(project_scores)
            / len(project_scores)
        )

    else:

        project_relevance = 0.0

    if project_skill_scores:

        project_skill_relevance = (
            sum(project_skill_scores)
            / len(project_skill_scores)
        )

    else:

        project_skill_relevance = 0.0

    # --------------------------------------------------
    # 4. Evidence presence
    # --------------------------------------------------

    experience_presence = (
        min(
            len(resume_experience),
            2
        ) / 2
    ) * 100

    project_presence = (
        min(
            len(resume_projects),
            2
        ) / 2
    ) * 100

    # --------------------------------------------------
    # 5. Overall evidence quality
    # --------------------------------------------------

    evidence_score = (

        skill_coverage * 0.35

        + experience_relevance * 0.20

        + project_relevance * 0.20

        + project_skill_relevance * 0.15

        + (
            (
                experience_presence
                + project_presence
            ) / 2
        ) * 0.10

    )

    evidence_score = max(
        0.0,
        min(
            100.0,
            evidence_score
        )
    )

    return {

        "score": round(
            evidence_score,
            2
        ),

        "skill_evidence": round(
            skill_coverage,
            2
        ),

        "experience_relevance": round(
            experience_relevance,
            2
        ),

        "project_relevance": round(
            project_relevance,
            2
        ),

        "project_skill_relevance": round(
            project_skill_relevance,
            2
        ),

        "has_experience": bool(
            resume_experience
        ),

        "experience_count": len(
            resume_experience
        ),

        "has_projects": bool(
            resume_projects
        ),

        "project_count": len(
            resume_projects
        )
    }