from fastapi import FastAPI

from app.api.v1 import router as api_v1
from app.core.config import settings

app = FastAPI(
    title="Task-Tracker API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(api_v1, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "API is up", "env": settings.db_url}
