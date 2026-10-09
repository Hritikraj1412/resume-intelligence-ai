
from sklearn.metrics.pairwise import cosine_similarity

from app.services.embedding_model import get_embedding_model


def calculate_semantic_similarity(
    resume_text: str,
    job_description: str
) -> float:
    """Calculate semantic similarity between a resume and a job."""

    resume_text = (resume_text or "").strip()
    job_description = (job_description or "").strip()

    # No meaningful comparison is possible with missing text.
    if not resume_text or not job_description:
        return 0.0

    model = get_embedding_model()

    embeddings = model.encode(
        [resume_text, job_description]
    )

    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    similarity = max(
        0.0,
        min(1.0, float(similarity))
    )

    return round(similarity * 100, 2)