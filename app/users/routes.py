from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.deps import get_db  # your session dependency
from . import crud as user_crud
from .schemas import UserCreate, UserOut, UserUpdate
from .models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_crud.create(db, user_in)


@router.get("/", response_model=List[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(User).options(selectinload(User.tasks), selectinload(User.projects))
    )
    return res.scalars().all()


@router.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await user_crud.get(db, user_id)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID, upd: UserUpdate, db: AsyncSession = Depends(get_db)
):
    db_user = await user_crud.get(db, user_id)
    return await user_crud.update(db, db_user, upd)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get(db, user_id)
    await user_crud.remove(db, db_user)
