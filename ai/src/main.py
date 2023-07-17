from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI

from router import router

app = FastAPI()
app.include_router(router)


@app.get("/healthz")
async def healthz():
    return "healthy"


app.mount("/", StaticFiles(directory="/static"), name="static")
