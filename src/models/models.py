import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator

ALLOWED_STATUS = {"todo", "in_progress", "done"}


def _validate_status(v: str) -> str:
    if v is None:
        return v
    if v not in ALLOWED_STATUS:
        raise ValueError(f"status 必须是 {ALLOWED_STATUS} 之一")
    return v


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    status: str = Field(default="todo")

    _check_status = field_validator("status")(_validate_status)

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)

    _check_status = field_validator("status")(_validate_status)


class Task(BaseModel):
    id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    status: str = Field(default="todo")
    created_at: datetime
    updated_at: datetime

    _check_status = field_validator("status")(_validate_status)


class TaskStorage:

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def create(self, data: TaskCreate) -> Task:
        task_id = str(uuid.uuid4())
        now = self._now()
        task = Task(
            id=task_id,
            title=data.title,
            description=data.description,
            status=data.status,
            created_at=now,
            updated_at=now,
        )
        self._tasks[task_id] = task
        return task

    def list_all(self) -> list[Task]:
        return list(self._tasks.values())


    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)


    def update(self, task_id: str, data: TaskUpdate) -> Optional[Task]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        update_data = data.model_dump(exclude_unset=True)
        updated = task.model_copy(update=update_data)
        updated.updated_at = self._now()
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: str) -> bool:
        if task_id in self._tasks:
           del self._tasks[task_id]
           return True
        return False
    

    


storage = TaskStorage()