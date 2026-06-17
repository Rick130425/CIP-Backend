from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment: str = "development"

    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"

    database_url: str = "sqlite:///./data/cip.db"

    data_dir: str = "./data"
    upload_dir: str = "./data/uploads"
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_name: str = "contracts"

    max_upload_size_mb: int = 20

    backend_cors_origins: str = "http://localhost:8501"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.backend_cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()