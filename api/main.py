
from fastapi import FastAPI
import asyncpg
import os

from .projects import router as projects_router
from .security import router as security_router

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres")

@app.on_event("startup")
async def startup():
    app.state.db = await asyncpg.create_pool(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()

@app.get("/")
async def root():
    return {"message": "magllama API is running"}

app.include_router(projects_router)
app.include_router(security_router)
