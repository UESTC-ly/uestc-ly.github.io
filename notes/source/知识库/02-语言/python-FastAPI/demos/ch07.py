from fastapi import APIRouter, FastAPI

router = APIRouter(prefix="/tasks", tags=["任务"])

@router.get("")
def list_tasks():
    return [{"id": 1, "title": "拆分路由"}]

app = FastAPI()
app.include_router(router, prefix="/api/v1")
