from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.tasks.schemas import TaskOut


class ProjectBase(BaseModel):
    name: str
    description: str


class ProjectCreate(ProjectBase):
    owner_id: UUID


class ProjectUpdate(BaseModel):
    name: str | None
    description: str | None


class ProjectAssignTask(BaseModel):
    project_id: UUID
    task_id: UUID


class ProjectOut(ProjectBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    tasks: list["TaskOut"] = []

    model_config = ConfigDict(from_attributes=True)
