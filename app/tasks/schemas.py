from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    name: str
    description: str | None
    deadline: date | None


class TaskCreate(TaskBase):
    owner_id: UUID


class TaskUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    complete: bool | None = None
    set_deadline: bool | None = None
    deadline: date | None = None


class TaskOut(TaskBase):
    id: UUID
    complete: bool
    created_at: datetime
    updated_at: datetime
    owner_id: UUID

    class Config:
        orm_mode = True
