from contextlib import asynccontextmanager
from time import perf_counter
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ready = True
    yield
    app.state.ready = False

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
    expose_headers=["X-Process-Time"],
)

@app.middleware("http")
async def timer(request: Request, call_next):
    started = perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{perf_counter() - started:.6f}"
    return response

def log_event(message: str):
    print(f"后台任务: {message}")

@app.post("/events", status_code=202)
def events(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(log_event, "收到事件")
    return {"accepted": request.app.state.ready}
