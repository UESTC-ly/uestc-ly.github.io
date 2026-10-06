from typing import Annotated
from fastapi import FastAPI, Path, Query

app = FastAPI()

@app.get("/tasks/search")
def search(q: Annotated[str, Query(min_length=1)]):
    return {"q": q}

@app.get("/tasks/{task_id}")
def read_task(
    task_id: Annotated[int, Path(gt=0)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    keyword: str | None = None,
):
    return {"task_id": task_id, "limit": limit, "keyword": keyword}
