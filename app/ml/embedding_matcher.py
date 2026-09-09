from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.
    """

    return SentenceTransformer(
        MODEL_NAME
    )


def semantic_similarity(
    resume_text: str,
    job_text: str,
) -> float:
    """
    Calculate semantic similarity between
    a resume and a job description.

    Returns a score from 0 to 100.
    """

    resume_text = resume_text.strip()
    job_text = job_text.strip()

    if not resume_text or not job_text:
        return 0.0

    model = get_embedding_model()

    embeddings = model.encode(
        [
            resume_text,
            job_text,
        ],
        normalize_embeddings=True,
    )

    similarity = cosine_similarity(
        embeddings[0:1],
        embeddings[1:2],
    )[0][0]

    similarity = max(
        0.0,
        min(1.0, float(similarity)),
    )

    return round(
        similarity * 100,
        2,
    )
