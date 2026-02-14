from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from app.core.config import settings
from app.models.mongo_models import URLModel

class Database:
    client: AsyncIOMotorClient = None
    db = None
    redis: Redis = None

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db.db = db.client[settings.MONGODB_DB_NAME]
    db.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    # This acts as your migration: Create a unique index on short_id
    await db.db[URLModel.Settings.collection_name].create_index(
        "short_id", unique=True
    )

async def close_mongo_connection():
    if db.client:
        db.client.close()
    if db.redis:
        await db.redis.close()