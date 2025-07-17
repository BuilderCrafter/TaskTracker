from app.core.exceptions import NotFoundError, ConflictError, ForbiddenError


class ProjectNotFoundError(NotFoundError):
    message = "Project not found"


class AlreadyAssignedError(ConflictError):
    message = "Task already belongs to this project"


class NotAssignedError(ConflictError):
    message = "Task doesn't belong to this project"


class OwnerMismatchError(ForbiddenError):
    message = "Project and task belong to different owners"
