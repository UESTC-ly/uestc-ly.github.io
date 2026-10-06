import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/wait")
async def wait():
    await asyncio.sleep(0.1)
    return {"done": True}

@app.get("/stream")
async def stream():
    async def chunks():
        for word in ["你好", "，", "FastAPI"]:
            await asyncio.sleep(0.1)
            yield word + "\n"
    return StreamingResponse(chunks(), media_type="text/plain")
