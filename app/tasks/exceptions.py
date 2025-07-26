# app/tasks/exceptions.py
from __future__ import annotations


from app.core.exceptions import (
    TaskTrackerError,
    NotFoundError,
    AlreadyExistsError,
    ConflictError,
    BadRequestError,
    ForbiddenError,
)


# ── Package-root for easy filtering / logging ───────────────────
class TaskError(TaskTrackerError):
    """Root for all task-related errors."""


# ── Look-ups ─────────────────────────────────────────────────────
class TaskNotFoundError(NotFoundError, TaskError):
    """Task id does not exist."""

    message = "Task not found"


# ── Create / uniqueness ─────────────────────────────────────────
class TaskAlreadyExistsError(AlreadyExistsError, TaskError):
    """Duplicate primary-key or unique field (e.g. name per owner)."""

    message = "Task already exists"


# ── State invariants ─────────────────────────────────────────–––
class TaskAlreadyCompletedError(ConflictError, TaskError):
    """
    Attempts to mark a task complete when it is already complete,
    or to un-complete one that is already open.
    """

    message = "Task is already marked as complete"


class InvalidDeadlineError(BadRequestError, TaskError):
    """
    Deadline fails validation (e.g. in the past or before project start).
    """

    message = "Deadline must be today or in the future"


# ── Ownership / permission ──────────────────────────────────────
class TaskOwnerMismatchError(ForbiddenError, TaskError):
    """Acting user is not the owner (or lacks rights)."""

    message = "You are not allowed to modify this task"


# ── Assignment (optional – include if you manage it from task side) ─
class TaskAlreadyAssignedError(ConflictError, TaskError):
    """
    Raised when code on the *task* side (not project.add_task) tries to
    assign it to a project it already belongs to.
    """

    message = "Task is already assigned to this project"
