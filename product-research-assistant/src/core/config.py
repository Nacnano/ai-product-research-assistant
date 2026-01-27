"""
Configuration module for the AI Product Research Assistant.

This module defines all configuration settings for the application including:
- API keys for LLM providers (OpenAI, Google)
- Database and vector store paths
- Search API configurations
- LLM provider selection

All settings can be overridden via environment variables or .env file.
"""
import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.
    
    Attributes:
        PROJECT_NAME: Name of the project
        OPENAI_API_KEY: API key for OpenAI services
        CHROMA_PERSIST_DIRECTORY: Path to ChromaDB vector store directory
        DATA_PATH: Path to the product catalog CSV file
        SERPER_API_KEY: Optional API key for Serper web search
        TAVILY_API_KEY: Optional API key for Tavily web search
        GOOGLE_API_KEY: Optional API key for Google Gemini
        LLM_PROVIDER: LLM provider to use ("openai" or "google")
    """
    PROJECT_NAME: str = "AI Product Research Assistant"
    OPENAI_API_KEY: str
    # Path to ChromaDB vector store (default: project_root/data/chroma_db)
    CHROMA_PERSIST_DIRECTORY: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "data", 
        "chroma_db"
    )
    # Path to product catalog CSV file (default: project_root/data/products_catalog.csv)
    DATA_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
        "data", 
        "products_catalog.csv"
    )
    
    # Optional web search API keys - if not provided, mock search will be used
    SERPER_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    
    # LLM provider configuration
    GOOGLE_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "google"  # Options: "openai" or "google"

    class Config:
        env_file = ".env"

settings = Settings()
