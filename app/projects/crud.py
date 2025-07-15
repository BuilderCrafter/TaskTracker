from uuid import UUID
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Project
from .schemas import ProjectCreate, ProjectUpdate
from .exceptions import (
    ProjectNotFoundError,
    AlreadyAssignedError,
    OwnerMismatchError,
    NotAssignedError,
)

from app.users.models import User
from app.users.exceptions import UserNotFoundError

from app.tasks.models import Task
from app.tasks.exceptions import TaskNotFoundError


async def get(db: AsyncSession, project_id: UUID) -> Project:
    res_project = await db.execute(select(Project).where(Project.id == project_id))
    project: Project | None = res_project.scalar_one_or_none()
    if project is None:
        raise ProjectNotFoundError(ctx={"id": str(project_id)})
    return project


async def get_by_name(db: AsyncSession, project_name: str) -> Sequence[Project]:
    tasks = await db.execute(
        select(Project).where(Project.name.ilike(f"%{project_name}%"))
    )
    return tasks.scalars().all()


async def create(db: AsyncSession, obj: ProjectCreate) -> Project:
    res_owner = await db.execute(select(User).where(User.id == obj.owner_id))
    owner: User | None = res_owner.scalar_one_or_none()
    if owner is None:
        raise UserNotFoundError(ctx={"id": str(obj.owner_id)})

    db_obj = Project(name=obj.name, description=obj.description, owner_id=obj.owner_id)
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_obj)
    return db_obj


async def update(db: AsyncSession, db_obj: Project, obj: ProjectUpdate) -> Project:
    if obj.name is not None:
        db_obj.name = obj.name
    if obj.description is not None:
        db_obj.description = obj.description

    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def add_task(db: AsyncSession, task_id: UUID, project_id: UUID) -> Project:
    res_task = await db.execute(select(Task).where(Task.id == task_id))
    task: Task | None = res_task.scalar_one_or_none()
    if task is None:
        raise TaskNotFoundError(ctx={"id": str(task_id)})

    res_project = await db.execute(select(Project).where(Project.id == project_id))
    project: Project | None = res_project.scalar_one_or_none()
    if project is None:
        raise ProjectNotFoundError(ctx={"id": str(project_id)})

    if task.project_id == project.id:
        raise AlreadyAssignedError(
            ctx={"project_id": str(project_id), "task_id": str(task_id)}
        )

    if project.owner_id != task.owner_id:
        raise OwnerMismatchError(
            ctx={
                "project_owner_id": str(project.owner_id),
                "task_owner_id": str(task.owner_id),
            }
        )

    project.tasks.append(task)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise

    await db.refresh(project)
    return project


async def remove_task(db: AsyncSession, task_id: UUID, project_id: UUID) -> Project:
    res_task = await db.execute(select(Task).where(Task.id == task_id))
    task: Task | None = res_task.scalar_one_or_none()
    if task is None:
        raise TaskNotFoundError(ctx={"id": str(task_id)})

    res_project = await db.execute(select(Project).where(Project.id == project_id))
    project: Project | None = res_project.scalar_one_or_none()
    if project is None:
        raise ProjectNotFoundError(ctx={"id": str(project_id)})

    if task.project_id != project.id or task.project_id is None:
        raise NotAssignedError(
            ctx={"project_id": str(project.id), "task_id": str(task.id)}
        )

    project.tasks.remove(task)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise

    await db.refresh(project)
    return project


async def remove(db: AsyncSession, db_obj: Project) -> None:
    await db.delete(db_obj)
    await db.commit()
