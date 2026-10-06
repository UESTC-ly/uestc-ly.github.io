from contextlib import asynccontextmanager
from pathlib import Path
from tempfile import gettempdir
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Response
from pydantic import BaseModel, Field as PydanticField
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str

class TaskInput(BaseModel):
    title: str = PydanticField(min_length=1, max_length=50)

class TaskOut(BaseModel):
    id: int
    title: str

db_path = Path(gettempdir()) / "fastapi-notes-tasks.db"
engine = create_engine(
    f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
    engine.dispose()

app = FastAPI(lifespan=lifespan)

def get_session():
    with Session(engine) as session:
        yield session

DB = Annotated[Session, Depends(get_session)]

def get_task_or_404(task_id: int, session: Session):
    task = session.get(Task, task_id)
    if task is None:
        raise HTTPException(404, "任务不存在")
    return task

@app.post("/tasks", response_model=TaskOut, status_code=201)
def create_task(data: TaskInput, session: DB):
    task = Task(**data.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks", response_model=list[TaskOut])
def list_tasks(session: DB):
    return session.exec(select(Task).order_by(Task.id)).all()

@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id: int, session: DB):
    return get_task_or_404(task_id, session)

@app.put("/tasks/{task_id}", response_model=TaskOut)
def replace_task(task_id: int, data: TaskInput, session: DB):
    task = get_task_or_404(task_id, session)
    task.title = data.title
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: DB):
    task = get_task_or_404(task_id, session)
    session.delete(task)
    session.commit()
    return Response(status_code=204)
