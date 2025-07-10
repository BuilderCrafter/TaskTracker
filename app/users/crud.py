from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from .models import User
from .schemas import UserCreate, UserUpdate

from app.tasks.models import Task


async def get(db: AsyncSession, user_id: UUID) -> User | None:
    res = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.tasks))
    )
    return res.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    res = await db.execute(
        select(User).where(User.email == email).options(selectinload(User.tasks))
    )
    return res.scalar_one_or_none()


async def create(db: AsyncSession, obj: UserCreate) -> User:
    db_obj = User(
        email=obj.email,
        full_name=obj.full_name,
        hashed_pass=get_password_hash(obj.password),
    )
    db.add(db_obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_obj)
    return db_obj


async def update(db: AsyncSession, db_obj: User, obj: UserUpdate) -> User:
    if obj.full_name is not None:
        db_obj.full_name = obj.full_name
    if obj.password is not None:
        db_obj.hashed_pass = get_password_hash(obj.password)
    if obj.is_active is not None:
        db_obj.is_active = obj.is_active

    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def remove(db: AsyncSession, db_obj: User) -> None:
    await db.delete(db_obj)
    await db.commit()


async def assign_task(db: AsyncSession, owner_id: UUID, task_id: UUID) -> User:
    res_task = await db.execute(select(Task).where(Task.id == task_id))
    task: Task | None = res_task.scalar_one_or_none()
    if task is None:
        raise ValueError(f"Task<{task_id}> not found")

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
    return user


async def remove_task(db: AsyncSession, owner_id: UUID, task_id: UUID) -> User:
    res_task = await db.execute(select(Task).where(Task.id == task_id))
    task: Task | None = res_task.scalar_one_or_none()
    if task is None:
        raise ValueError(f"Task<{task_id}> not found")

    res_user = await db.execute(select(User).where(User.id == owner_id))
    user: User | None = res_user.scalar_one_or_none()
    if user is None:
        raise ValueError(f"User<{owner_id}> not found")

    if task.owner_id != owner_id:
        raise ValueError(f"Task<{task_id}> not owner by User<{owner_id}>")
    task.owner = None
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise

    await db.refresh(task)
    return user
