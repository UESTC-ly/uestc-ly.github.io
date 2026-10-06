from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()

class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(min_length=1, max_length=30)
    priority: int = Field(default=1, ge=1, le=3)
    tags: list[str] = Field(default_factory=list)

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    return task.model_dump()
