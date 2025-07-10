from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    name: str
    description: str | None
    deadline: date | None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    complete: bool | None = None
    set_deadline: bool | None = None
    deadline: date | None = None


class OwnerAssign(BaseModel):
    task_id: UUID
    owner_id: UUID | None


class TaskOut(TaskBase):
    id: UUID
    complete: bool
    created_at: datetime
    updated_at: datetime
    owner_id: UUID | None

    class Config:
        orm_mode = True
