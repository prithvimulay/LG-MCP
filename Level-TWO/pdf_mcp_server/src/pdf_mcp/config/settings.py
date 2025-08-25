from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    """Application settings with validation"""
    
    pdf_storage_path: Path = Field(default_factory=lambda: Path("src/data/pdfs"))
    vector_db_path: Path = Field(default_factory=lambda: Path("src/vector_db"))
    podcast_storage_path: Path = Field(default_factory=lambda: Path("src/data/podcasts"))
    audio_storage_path: Path = Field(default_factory=lambda: Path("src/data/audio"))
    
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    groq_api_key: str = Field(default="", description="GROQ API key for LLM")
    openai_api_key: str = Field(default="", description="OpenAI API key (optional)")
    
    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "llama3-70b-8192"
    llm_temperature: float = 0.2
    
    mcp_server_name: str = "pdf-mcp-server"
    mcp_server_version: str = "2.0.0"
    
    # LangSmith configuration
    langsmith_tracing: bool = Field(default=False, description="Enable LangSmith tracing")
    langsmith_endpoint: str = Field(default="https://api.smith.langchain.com", description="LangSmith API endpoint")
    langsmith_api_key: Optional[str] = Field(default=None, description="LangSmith API key")
    langsmith_project: str = Field(default="pdf-lg-mcp-smith", description="LangSmith project name")
    
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @field_validator("groq_api_key")
    @classmethod
    def validate_groq_api_key(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("GROQ_API_KEY is required. Set it in .env file or environment variable.")
        return v.strip()

    @field_validator("pdf_storage_path", "vector_db_path", "podcast_storage_path", "audio_storage_path")
    @classmethod
    def validate_and_create_paths(cls, v: Path) -> Path:
        if isinstance(v, str):
            v = Path(v)
        resolved_path = v.expanduser().resolve()
        resolved_path.mkdir(parents=True, exist_ok=True)
        return resolved_path

settings = Settings()
