from sklearn.metrics.pairwise import cosine_similarity
from app.services.embedding_model import get_embedding_model
from app.services.embedding_model import get_embedding_model
from app.services.skill_extractor import extract_skills


def calculate_project_relevance(
    projects: list[dict],
    required_skills: list[str],
    responsibilities: list[str]
) -> dict:

    if not projects:
        return {
            "score": 0.0,
            "projects": []
        }

    model = get_embedding_model()

    required_skill_set = {
        skill.lower()
        for skill in required_skills
    }

    responsibility_text = " ".join(
        responsibilities
    ).strip()

    results = []

    for project in projects:

        project_name = project.get(
            "name",
            "Unnamed Project"
        )

        project_description = project.get(
            "description",
            ""
        )

        project_text = (
            project_name
            + ". "
            + project_description
        ).strip()

        detected_skills = set(
            skill.lower()
            for skill in extract_skills(project_text)
        )

        matched_skills = sorted(
            detected_skills.intersection(
                required_skill_set
            )
        )

        if required_skill_set:
            skill_score = (
                len(matched_skills)
                / len(required_skill_set)
            ) * 100
        else:
            skill_score = 0.0

        if responsibility_text:

            embeddings = model.encode([
                project_text,
                responsibility_text
            ])

            semantic_score = cosine_similarity(
                [embeddings[0]],
                [embeddings[1]]
            )[0][0] * 100

            semantic_score = max(
                0.0,
                min(
                    100.0,
                    float(semantic_score)
                )
            )

        else:
            semantic_score = 0.0

        project_score = (
            (skill_score * 0.40)
            + (semantic_score * 0.60)
        )

        results.append({
            "project": project_name,
            "matched_skills": matched_skills,
            "skill_score": round(
                skill_score,
                2
            ),
            "semantic_score": round(
                semantic_score,
                2
            ),
            "score": round(
                project_score,
                2
            )
        })

    if results:

        overall_score = (
            sum(
                project["score"]
                for project in results
            )
            / len(results)
        )

    else:
        overall_score = 0.0

    return {
        "score": round(
            overall_score,
            2
        ),
        "projects": results
    }