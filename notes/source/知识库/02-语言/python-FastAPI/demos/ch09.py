from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

app = FastAPI()
bearer = HTTPBearer(auto_error=False)

def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
):
    if credentials is None or credentials.credentials != "demo-token":
        raise HTTPException(
            status_code=401,
            detail="凭证缺失或无效",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"id": 1, "name": "学习者"}

@app.get("/me")
def me(user: Annotated[dict, Depends(current_user)]):
    return user
