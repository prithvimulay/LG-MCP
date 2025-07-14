from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from pathlib import Path


class Settings(BaseSettings):
    pdf_storage_path: Path
    vector_db_path: Path
    podcast_storage_path: Path

    chunk_size: int = 1000
    chunk_overlap: int = 200
    mcp_server_name: str = "pdf-mcp-server"
    podcast_max_duration: int = 30
    podcast_chunk_limit: int = 10
    audio_language: str = "en"
    audio_speed: float = 1.0
    audio_format: str = "mp3"
    groq_api_key: str = ""
    openai_api_key: str = ""
    embedding_model: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env"
    )

    @field_validator("pdf_storage_path", "vector_db_path", "podcast_storage_path", mode="before")
    @classmethod
    def resolve_path(cls, v: str | Path) -> Path:
        return Path(v).expanduser().resolve()


def get_settings() -> Settings:
    return Settings()

settings = get_settings()


if __name__ == "__main__":
    print("PDF path:", settings.pdf_storage_path)
    print("Vector DB path:", settings.vector_db_path)
