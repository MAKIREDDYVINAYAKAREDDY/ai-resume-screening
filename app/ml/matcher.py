from sklearn.feature_extraction.text import (
    TfidfVectorizer,
)

from sklearn.metrics.pairwise import (
    cosine_similarity,
)


def semantic_similarity(
    resume_text: str,
    job_text: str,
) -> float:

    if (
        not resume_text.strip()
        or not job_text.strip()
    ):
        return 0.0

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
    )

    matrix = vectorizer.fit_transform(
        [
            resume_text,
            job_text,
        ]
    )

    similarity = cosine_similarity(
        matrix[0:1],
        matrix[1:2],
    )[0][0]

    return round(
        float(similarity) * 100,
        2,
    )
