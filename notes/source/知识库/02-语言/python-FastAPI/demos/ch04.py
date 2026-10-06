from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
records = {1: {"id": 1, "title": "复习", "internal_note": "内部字段"}}

class TaskOut(BaseModel):
    id: int
    title: str

@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id: int):
    if task_id not in records:
        raise HTTPException(status_code=404, detail="任务不存在")
    return records[task_id]
