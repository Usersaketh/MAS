from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MAS Query System"
    app_version: str = "0.1.0"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_embed_model: str = "nomic-embed-text"

    vector_dimension: int = 384
    faiss_index_path: str = "./data/faiss.index"
    faiss_metadata_path: str = "./data/documents.json"

    # Stage 3: Agent thresholds and policy rules
    escalation_confidence_threshold: float = 0.6
    max_refund_days: int = 30
    max_cancellation_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
