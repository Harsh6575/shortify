from fastapi import FastAPI
from app.core.db import engine, Base, redis_client, mongo_client

app = FastAPI(title="Shortify")

@app.on_event("startup")
async def startup():
    # Create tables
    async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)
    print("✅ Databases initialized successfully.")

@app.on_event("shutdown")
async def shutdown():
    await redis_client.close()
    mongo_client.close()
    print("🛑 Databases connections closed.")

@app.get("/")
def root():
    return {"message": "Shortify backend is running 🚀"}
