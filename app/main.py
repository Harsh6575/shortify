from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.db import close_mongo_connection, connect_to_mongo
from app.api.v1.api import api_router
from app.api.v1.urls import redirect_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(title="Shortify", lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")
app.include_router(redirect_router)

@app.get("/")
def root():
    return {"message": "Shortify backend is running 🚀"}