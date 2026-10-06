from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_tfidf_similarity(
    resume_text: str,
    job_description: str
) -> float:

    documents = [
        resume_text,
        job_description
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        vectors[0],
        vectors[1]
    )[0][0]

    return round(float(similarity) * 100, 2)