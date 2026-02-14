from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.db import close_mongo_connection, connect_to_mongo
from app.api.v1.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB and Redis
    await connect_to_mongo()
    yield
    # Shutdown: Close connections
    await close_mongo_connection()

app = FastAPI(title="Shortify", lifespan=lifespan)

# Include routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Shortify backend is running 🚀"}