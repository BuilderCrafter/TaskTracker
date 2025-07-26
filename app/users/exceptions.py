from http import HTTPStatus

from app.core.exceptions import (
    ErrorCode,
    NotFoundError,
    AlreadyExistsError,
    BadRequestError,
    ForbiddenError,
    TaskTrackerError,
)


class UserError(TaskTrackerError):
    """Root for user-domain errors."""


class UserNotFoundError(NotFoundError, UserError):
    message = "User not found"


class EmailAlreadyExistsError(AlreadyExistsError, UserError):
    message = "E-mail address is already in use"


class InvalidCredentialsError(BadRequestError, UserError):
    http_status = HTTPStatus.UNAUTHORIZED  # override 400 → 401
    code = ErrorCode.UNAUTHORIZED
    message = "Invalid e-mail or password"


class UserDeletionForbiddenError(ForbiddenError, UserError):
    message = "You are not allowed to delete this user"
