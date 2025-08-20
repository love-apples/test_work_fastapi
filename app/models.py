from uuid import uuid4, UUID

from beanie import Document
from pydantic import Field

from app.enums import TaskStatus


class TaskModel(Document):
    id: UUID = Field(default_factory=uuid4) # type: ignore
    title: str
    description: str
    status: TaskStatus

    class Settings:
        name = 'tasks'