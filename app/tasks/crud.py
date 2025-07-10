from uuid import UUID
from typing import Sequence, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Task
from .schemas import TaskCreate, TaskUpdate

from app.users.models import User


async def get(db: AsyncSession, task_id: UUID) -> Task | None:
    task = await db.execute(select(Task).where(Task.id == task_id))
    return task.scalar_one_or_none()


async def get_by_name(db: AsyncSession, task_name: str) -> Sequence[Task]:
    tasks = await db.execute(select(Task).where(Task.name.ilike(f"%{task_name}%")))
    return tasks.scalars().all()


async def create(db: AsyncSession, obj: TaskCreate) -> Task:
    db_obj = Task(name=obj.name, description=obj.description, deadline=obj.deadline)
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_obj)
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


async def assign_owner(
    db: AsyncSession, task_id: UUID, owner_id: Optional[UUID]
) -> Task:
    res_task = await db.execute(select(Task).where(Task.id == task_id))
    task: Task | None = res_task.scalar_one_or_none()
    if task is None:
        raise ValueError(f"Task<{task_id}> not found")

    if owner_id is not None:
        res_user = await db.execute(select(User).where(User.id == owner_id))
        user: User | None = res_user.scalar_one_or_none()
        if user is None:
            raise ValueError(f"User<{owner_id}> not found")

    task.owner = user
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise

    await db.refresh(task)
    if user is not None:
        await db.refresh(user)
    return task


async def remove(db: AsyncSession, db_obj: Task) -> None:
    await db.delete(db_obj)
    await db.commit()
