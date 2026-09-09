import ollama

from app.core.config import get_settings


settings = get_settings()


def get_ollama_client():
    if not settings.llm_enabled:
        raise RuntimeError("LLM_ENABLED is false.")

    if settings.llm_provider.lower() != "ollama":
        raise RuntimeError(
            f"LLM provider is '{settings.llm_provider}', not 'ollama'."
        )

    return ollama.Client(
        host=settings.ollama_base_url
    )


def get_ollama_model() -> str:
    return settings.ollama_model
