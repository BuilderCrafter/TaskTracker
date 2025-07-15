from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from .models import User
from .schemas import UserCreate, UserUpdate
from .exceptions import EmailAlreadyExistsError, UserNotFoundError


async def get(db: AsyncSession, user_id: UUID) -> User:
    res_user = await db.execute(
        select(User).where(User.id == user_id).options(selectinload(User.tasks))
    )
    user: User | None = res_user.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError(ctx={"id": str(user_id)})
    return user


async def get_by_email(db: AsyncSession, email: str) -> User:
    res_user = await db.execute(
        select(User).where(User.email == email).options(selectinload(User.tasks))
    )
    user: User | None = res_user.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError(ctx={"email": str(email)})
    return user


async def create(db: AsyncSession, obj: UserCreate) -> User:

    res_user = await db.execute(select(User).where(User.email == obj.email))
    user: User | None = res_user.scalar_one_or_none()
    if user:
        raise EmailAlreadyExistsError(ctx={"email": str(obj.email)})

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
        db_obj.hashed_pass = get_password_hash(str(obj.password))
    if obj.is_active is not None:
        db_obj.is_active = obj.is_active

    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def remove(db: AsyncSession, db_obj: User) -> None:
    await db.delete(db_obj)
    await db.commit()
