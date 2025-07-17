from fastapi import FastAPI

from app.api.v1 import router as api_v1
from app.api.exception_handler import register_exception_handlers
from app.core.config import settings
from app.users.routes import router as user_router
from app.tasks.routes import router as task_router

app = FastAPI(
    title="Task-Tracker API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(api_v1, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(task_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "API is up", "env": settings.db_url}


register_exception_handlers(app)
