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

    class Config:
        env_file = ".env"

settings = Settings()
