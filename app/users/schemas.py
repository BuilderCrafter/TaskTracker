from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.tasks.schemas import TaskOut
from app.projects.schemas import ProjectOut


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None


class UserOut(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    projects: list[ProjectOut] = []
    tasks: list[TaskOut] = []

    model_config = ConfigDict(from_attributes=True)
