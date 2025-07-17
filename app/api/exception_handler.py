from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.core.exceptions import TaskTrackerError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TaskTrackerError)
    async def _task_tracker_error(_, exc: TaskTrackerError):
        return JSONResponse(status_code=exc.http_status, content=exc.to_dict())
