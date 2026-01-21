from fastapi import FastAPI
from src.api.routes import router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Product Research Assistant API",
    version="1.0.0"
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
