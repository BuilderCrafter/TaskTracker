from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from .models import User
from .schemas import UserCreate, UserUpdate


async def get(db: AsyncSession, user_id: UUID) -> User | None:
    res = await db.execute(select(User).where(User.id == user_id))
    return res.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    res = await db.execute(select(User).where(User.email == email))
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
