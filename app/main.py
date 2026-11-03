#main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_tables
from crud import router as crud_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application starting up...")
    create_tables()
    yield
    print("Application shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(crud_router)

