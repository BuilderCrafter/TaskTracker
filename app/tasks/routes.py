from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db
from .schemas import TaskOut, TaskCreate, TaskUpdate
from .models import Task
from . import crud as task_crud

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await task_crud.create(db, task_in)


@router.get("/", response_model=List[TaskOut])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Task))
    return res.scalars().all()


@router.get("/{task_name}", response_model=List[TaskOut])
async def get_task_by_name(task_name: str, db: AsyncSession = Depends(get_db)):
    return await task_crud.get_by_name(db, task_name)


@router.get("/{task_id}", response_model=TaskOut)
async def get_task_by_id(task_id: UUID, db: AsyncSession = Depends(get_db)):
    return await task_crud.get(db, task_id)


@router.patch("/update/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: UUID, task_in: TaskUpdate, db: AsyncSession = Depends(get_db)
):
    db_task = await task_crud.get(db, task_id)
    return await task_crud.update(db, db_task, task_in)


@router.delete("/delete/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID, db: AsyncSession = Depends(get_db)):
    db_task = await task_crud.get(db, task_id)
    await task_crud.remove(db, db_task)
