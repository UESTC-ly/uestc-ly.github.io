from typing import Annotated
from fastapi import Depends, FastAPI, Query

app = FastAPI()

def pagination(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
):
    return {"offset": offset, "limit": limit}

Page = Annotated[dict, Depends(pagination)]

@app.get("/tasks")
def tasks(page: Page):
    data = ["读书", "写代码", "复习"]
    return data[page["offset"]:page["offset"] + page["limit"]]
