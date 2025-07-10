from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db
from .schemas import TaskOut, TaskCreate, TaskUpdate
from .models import Task
from . import crud as task_crud
from app.users import crud as user_crud

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await task_crud.create(db, task_in)


@router.get("/", response_model=List[TaskOut])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Task))
    return res.scalars().all()


@router.get("/{task_id}", response_model=TaskOut)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    db_task = await task_crud.get(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail=f"Task<{task_id}> not found")
    return db_task


@router.patch("/{task_id}/update", response_model=TaskOut)
async def update_task(
    task_id: UUID, task_in: TaskUpdate, db: AsyncSession = Depends(get_db)
):
    db_task = await task_crud.get(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail=f"Task<{task_id}> not found")
    return await task_crud.update(db, db_task, task_in)


@router.patch("/{task_id}/assign", response_model=TaskOut)
async def assign_owner(
    task_id: UUID, owner_id: UUID | None, db: AsyncSession = Depends(get_db)
):
    db_task = await task_crud.get(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail=f"Task<{task_id}> not found")
    if owner_id:
        db_user = await user_crud.get(db, owner_id)
        if db_user is None:
            raise HTTPException(status_code=404, detail=f"User<{owner_id} not found")
    return await task_crud.assign_owner(db, task_id, owner_id)


@router.delete("/{task_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    db_task = await task_crud.get(db, task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail=f"Task<{task_id}> not found")
    await task_crud.remove(db, db_task)
