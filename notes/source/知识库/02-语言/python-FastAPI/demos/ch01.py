from fastapi import FastAPI

app = FastAPI(title="FastAPI 最小示例")

@app.get("/hello")
def hello():
    return {"message": "Hello FastAPI"}
