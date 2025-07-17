from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db
from .schemas import ProjectOut, ProjectCreate, ProjectUpdate
from .models import Project
from . import crud as project_crud

from app.tasks import crud as task_crud

router = APIRouter(prefix="/projects", tags=["tasks"])


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(project_in: ProjectCreate, db: AsyncSession = Depends(get_db)):
    return await project_crud.create(db, project_in)


@router.get("/", response_model=List[ProjectOut])
async def list_project(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Project))
    return res.scalars().all()


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    db_project = await project_crud.get(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail=f"Project<{project_id}> not found")
    return db_project


@router.patch("/{project_id}/update", response_model=ProjectOut)
async def update_project(
    project_id: UUID, project_in: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    db_project = await project_crud.get(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail=f"Project<{project_id}> not found")
    return await project_crud.update(db, db_project, project_in)


@router.patch("/{project_id}/assign{task_id}", response_model=ProjectOut)
async def assing_project(
    project_id: UUID, task_id: UUID, db: AsyncSession = Depends(get_db)
):

    db_project = await project_crud.get(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail=f"Project<{project_id}> not found")

    db_task = await task_crud.get(db=db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail=f"Task<{task_id}> not found")

    return await project_crud.add_task(db=db, task_id=task_id, project_id=project_id)


@router.delete("/delete/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    db_project = await project_crud.get(db, project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail=f"Project<{project_id}> not found")
    await project_crud.remove(db, db_project)
