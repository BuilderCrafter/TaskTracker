from enum import Enum
from http import HTTPStatus
from typing import Any, Mapping


class ErrorCode(str, Enum):
    """Error identifiers used across the whole code."""

    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    FORBIDDEN = "FORBIDDEN"
    BAD_REQUEST = "BAD_REQUEST"
    CONFLICT = "CONFLICT"
    UNAUTHORIZED = "UNAUTHORIZED"
    INTERNAL = "INTERNAL"  # fallback


class TaskTrackerError(Exception):
    """
    Root for all domain errors.
    code : ErrorCode - Stable identifier log aggregation, client branching etc.
    message : str - Human-readable sentence.
    http_status : HTTPStatus - Which response status the API should emit.
    ctx : dict[str, Any] | None - Extra context (ids, params) – for structured logging / telemetry. *Never* put sensitive data here; this dict may be logged verbatim.
    """

    code: ErrorCode = ErrorCode.INTERNAL
    http_status: HTTPStatus | int = HTTPStatus.INTERNAL_SERVER_ERROR
    message: str = "An internal error occurred"
    ctx: Mapping[str, Any] | None = None

    def __init__(
        self,
        *,
        message: str | None = None,
        ctx: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(message or self.message)
        if message:  # allow per-instance override
            self.message = message
        if ctx:
            self.ctx = ctx

    def to_dict(self) -> dict[str, Any]:
        """
        Serialise for JSON responses or logs.
        """
        return {
            "code": self.code,
            "message": self.message,
            "context": self.ctx,
        }

    def __repr__(self) -> str:  # prettier log lines
        return (
            f"{self.__class__.__name__}(code={self.code!s}, "
            f"message={self.message!r}, ctx={self.ctx!r})"
        )


# Shared *status* subclasses (import these everywhere)
class NotFoundError(TaskTrackerError):
    code = ErrorCode.NOT_FOUND
    http_status = HTTPStatus.NOT_FOUND
    message = "Resource not found"


class BadRequestError(TaskTrackerError):
    code = ErrorCode.BAD_REQUEST
    http_status = HTTPStatus.BAD_REQUEST
    message = "Bad request"


class ForbiddenError(TaskTrackerError):
    code = ErrorCode.FORBIDDEN
    http_status = HTTPStatus.FORBIDDEN
    message = "Action not allowed"


class UnauthorizedError(TaskTrackerError):
    code = ErrorCode.UNAUTHORIZED
    http_status = HTTPStatus.UNAUTHORIZED
    message = "Authentication required or failed"


class AlreadyExistsError(TaskTrackerError):
    code = ErrorCode.ALREADY_EXISTS
    http_status = HTTPStatus.CONFLICT
    message = "Resource already exists"


class ConflictError(TaskTrackerError):
    code = ErrorCode.CONFLICT
    http_status = HTTPStatus.CONFLICT
    message = "Conflict with current state"
