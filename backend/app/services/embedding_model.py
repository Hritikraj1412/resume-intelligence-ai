
import os
from functools import lru_cache

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the embedding model only when semantic matching is enabled."""

    if os.getenv("DISABLE_SEMANTIC_MODEL", "false").lower() == "true":
        return None

    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)