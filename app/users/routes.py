from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db  # your session dependency
from . import crud
from .schemas import UserCreate, UserOut, UserUpdate
from .models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    if await crud.get_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create(db, user_in)


@router.get("/", response_model=List[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User))
    return res.scalars().all()


@router.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID, upd: UserUpdate, db: AsyncSession = Depends(get_db)
):
    db_user = await crud.get(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return await crud.update(db, db_user, upd)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    await crud.remove(db, db_user)
