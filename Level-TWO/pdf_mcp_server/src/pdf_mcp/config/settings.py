from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    pdf_storage_path: Path = Path("./data/pdfs")
    vector_db_path: Path = Path("./vector_db")

    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # MCP Server Configuration
    mcp_server_name: str = "pdf-mcp-server"

    # Podcast Configuration
    podcast_storage_path: Path = Path("./data/podcasts")
    podcast_max_duration: int = 30  # minutes
    podcast_chunk_limit: int = 10  # max chunks to process per podcast

    # Audio Configuration
    audio_language: str = "en"
    audio_speed: float = 1.0
    audio_format: str = "mp3"

    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()

settings = Settings()
