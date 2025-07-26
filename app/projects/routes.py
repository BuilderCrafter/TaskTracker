from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.deps import get_db
from .schemas import ProjectOut, ProjectCreate, ProjectUpdate, ProjectAssignTask
from .models import Project
from . import crud as project_crud

router = APIRouter(prefix="/projects", tags=["tasks"])


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: ProjectCreate, db: AsyncSession = Depends(get_db)):
    return await project_crud.create(db, project_in)


@router.get("/", response_model=List[ProjectOut])
async def list_project(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Project).options(selectinload(Project.tasks)))
    return res.scalars().all()


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    return await project_crud.get(db, project_id)


@router.get("/name/{project_name}", response_model=List[ProjectOut])
async def get_project_by_name(project_name: str, db: AsyncSession = Depends(get_db)):
    return await project_crud.get_by_name(db, project_name)


@router.patch("/{project_id}", response_model=ProjectOut)
async def update_project(
    project_id: UUID, project_in: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    db_project = await project_crud.get(db, project_id)
    return await project_crud.update(db, db_project, project_in)


@router.patch("/{project_id}/assign/{task_id}", response_model=ProjectOut)
async def assing_project(
    assign_obj: ProjectAssignTask, db: AsyncSession = Depends(get_db)
):
    if assign_obj.task_assign:
        return await project_crud.add_task(
            db=db, task_id=assign_obj.task_id, project_id=assign_obj.project_id
        )
    else:
        return await project_crud.remove_task(
            db=db, task_id=assign_obj.task_id, project_id=assign_obj.project_id
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    await project_crud.remove(db, project_id)
