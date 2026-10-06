from fastapi import FastAPI
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DEMO_")
    app_name: str = "FastAPI 笔记"

settings = Settings()
app = FastAPI(title=settings.app_name)

@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
