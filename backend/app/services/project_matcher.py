
from sklearn.metrics.pairwise import cosine_similarity

from app.services.embedding_model import get_embedding_model
from app.services.skill_extractor import extract_skills
from app.services.skill_matcher import normalize_skill


def calculate_project_relevance(
    projects: list[dict],
    required_skills: list[str],
    responsibilities: list[str],
) -> dict:
    if not projects:
        return {"score": 0.0, "projects": []}

    required_skill_set = {
        normalize_skill(skill)
        for skill in (required_skills or [])
        if normalize_skill(skill)
    }

    responsibility_text = " ".join(
        responsibilities or []
    ).strip()

    model = get_embedding_model() if responsibility_text else None
    results = []

    for project in projects:
        project_name = project.get("name") or "Unnamed Project"
        project_description = project.get("description") or ""
        technologies = project.get("technologies") or []

        project_text = " ".join(
            part for part in [
                project_name,
                project_description,
                " ".join(technologies),
            ]
            if part
        ).strip()

        detected_skills = {
            normalize_skill(skill)
            for skill in (
                extract_skills(project_text) + technologies
            )
            if normalize_skill(skill)
        }

        matched_skills = sorted(
            required_skill_set.intersection(detected_skills)
        )

        skill_score = (
            len(matched_skills) / len(required_skill_set) * 100
            if required_skill_set
            else 0.0
        )

        semantic_score = 0.0
        if model is not None and project_text:
            embeddings = model.encode(
                [project_text, responsibility_text]
            )
            semantic_score = float(
                cosine_similarity(
                    [embeddings[0]],
                    [embeddings[1]],
                )[0][0] * 100
            )
            semantic_score = max(
                0.0, min(100.0, semantic_score)
            )

        project_score = (
            skill_score * 0.40
            + semantic_score * 0.60
        )

        results.append({
            "project": project_name,
            "description": project_description,
            "technologies": sorted(detected_skills),
            "matched_skills": matched_skills,
            "skill_score": round(skill_score, 2),
            "semantic_score": round(semantic_score, 2),
            "score": round(project_score, 2),
        })

    overall_score = sum(
        item["score"] for item in results
    ) / len(results)

    return {
        "score": round(overall_score, 2),
        "projects": results,
    }