from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.db import engine, Base, redis_client, mongo_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Databases initialized successfully.")
    
    yield  # Application runs here
    
    # Shutdown
    await redis_client.close()
    mongo_client.close()
    print("🛑 Database connections closed.")

app = FastAPI(title="Shortify", lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "Shortify backend is running 🚀"}