from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.deps import get_db  # your session dependency
from . import crud as user_crud
from .schemas import UserCreate, UserOut, UserUpdate
from .models import User
import app.tasks.crud as task_crud

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    if await user_crud.get_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_crud.create(db, user_in)


@router.get("/", response_model=List[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).options(selectinload(User.tasks)))
    return res.scalars().all()


@router.get("/{user_id}", response_model=UserOut)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User<{user_id}> not found")
    return db_user


@router.patch("/{user_id}/update", response_model=UserOut)
async def update_user(
    user_id: UUID, upd: UserUpdate, db: AsyncSession = Depends(get_db)
):
    db_user = await user_crud.get(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return await user_crud.update(db, db_user, upd)


@router.patch("/{user_id}/assign", response_model=UserOut)
async def add_task(user_id: UUID, task_id: UUID, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_task = await task_crud.get(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await user_crud.assign_task(db, db_user.id, db_task.id)


@router.patch("/{user_id}/unassign", response_model=UserOut)
async def remove_task(user_id: UUID, task_id: UUID, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_task = await task_crud.get(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await user_crud.remove_task(db, db_user.id, db_task.id)


@router.delete("/{user_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    db_user = await user_crud.get(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    await user_crud.remove(db, db_user)
