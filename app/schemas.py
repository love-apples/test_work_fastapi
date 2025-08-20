from __future__ import annotations

from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.enums import TaskStatus


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TaskCreateSchema(BaseSchema):
    title: str
    description: str
    

class TaskSchema(BaseSchema):
    id: UUID
    title: str
    description: str
    status: TaskStatus
    
    
class FetchTasksSchema(BaseSchema):
    tasks: List[TaskSchema]