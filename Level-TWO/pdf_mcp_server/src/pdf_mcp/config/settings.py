from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    mongodb_url: str = "mongodb+srv://notelm:notelm@cluster0.qzdd38m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    mongodb_database: str = "notelm"

    pdf_storage_path: Path = Path("./data/pdfs")
    temp_storage_path: Path = Path("./data/temp")
    chroma_db_path: Path = Path("./vector_db")

    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_results: int = 5

    mcp_server_name: str = "pdf-mcp-server"
    
    # LLM Configuration
    groq_api_key: str = ""  
    llm_model: str = "qwen-qwq-32b"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 4096
    
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

settings = Settings()
