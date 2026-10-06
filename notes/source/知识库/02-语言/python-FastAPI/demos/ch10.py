from typing import Annotated
from fastapi import FastAPI, File, Form, Header, UploadFile

app = FastAPI()

@app.post("/upload")
async def upload(
    file: Annotated[UploadFile, File()],
    note: Annotated[str, Form()] = "",
    x_request_id: Annotated[str | None, Header()] = None,
):
    size = 0
    try:
        while chunk := await file.read(64 * 1024):
            size += len(chunk)
        return {
            "filename": file.filename,
            "size": size,
            "note": note,
            "request_id": x_request_id,
        }
    finally:
        await file.close()
