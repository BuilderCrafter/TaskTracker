from uuid import UUID
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Task
from .schemas import TaskCreate, TaskUpdate
from .exceptions import TaskNotFoundError

from app.users.models import User
from app.users.exceptions import UserNotFoundError


async def get(db: AsyncSession, task_id: UUID) -> Task:
    res_task = await db.execute(select(Task).where(Task.id == task_id))
    task: Task | None = res_task.scalar_one_or_none()
    if task is None:
        raise TaskNotFoundError(ctx={"id": str(task_id)})
    return task


async def get_by_name(db: AsyncSession, task_name: str) -> Sequence[Task]:
    tasks = await db.execute(select(Task).where(Task.name.ilike(f"%{task_name}%")))
    return tasks.scalars().all()


async def create(db: AsyncSession, obj: TaskCreate) -> Task:
    res_owner = await db.execute(select(User).where(User.id == obj.owner_id))
    owner: User | None = res_owner.scalar_one_or_none()
    if owner is None:
        raise UserNotFoundError(ctx={"id": str(obj.owner_id)})

    db_obj = Task(
        name=obj.name,
        description=obj.description,
        deadline=obj.deadline,
        owner_id=obj.owner_id,
    )
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_obj)
    await db.refresh(owner)
    return db_obj


async def update(db: AsyncSession, db_obj: Task, obj: TaskUpdate) -> Task:
    if obj.name is not None:
        db_obj.name = obj.name
    if obj.description is not None:
        db_obj.description = obj.description
    if obj.complete is not None:
        db_obj.complete = obj.complete
    if obj.set_deadline is not None:
        db_obj.deadline = obj.deadline if obj.set_deadline else None

    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def remove(db: AsyncSession, db_obj: Task) -> None:
    await db.delete(db_obj)
    await db.commit()
