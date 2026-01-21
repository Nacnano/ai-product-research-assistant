import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Product Research Assistant"
    OPENAI_API_KEY: str
    CHROMA_PERSIST_DIRECTORY: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "chroma_db")
    DATA_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "products_catalog.csv")
    
    # Optional Real Search API Keys (if provided)
    SERPER_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    
    # LLM Settings
    GOOGLE_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"  # "openai" or "google"

    class Config:
        env_file = ".env"

settings = Settings()
