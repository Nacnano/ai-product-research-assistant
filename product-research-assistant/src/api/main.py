"""
FastAPI application entry point and configuration.

This module initializes the FastAPI application with:
- Application metadata (title, description, version)
- Router inclusion for API endpoints
- Lifespan event handlers for startup/shutdown tasks
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import router
from src.api.database import init_db
from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    
    Handles startup and shutdown events for the application.
    Initializes the database on startup.
    """
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: cleanup if needed (currently none required)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Product Research Assistant API for e-commerce product management",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
