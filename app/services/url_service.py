from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis
from app.models.mongo_models import URLModel
from fastapi import HTTPException
from app.utils.hash_generator import generate_short_id
import uuid

REDIS_STORE_TIME = 60 * 60 * 24  # 24 hours in seconds

class URLService:
    def __init__(self, database: AsyncIOMotorDatabase, redis: Redis): 
        self.collection = database[URLModel.Settings.collection_name]
        self.redis = redis
    
    async def create_short_url(self, full_url: str) -> URLModel: # , user_id: Optional[int] = None
        short_id = generate_short_id(str(full_url))
        # Loop to handle extremely rare hash collisions
        while True:
            existing_url = await self.collection.find_one({"short_id": short_id})
            if existing_url:
                if str(existing_url.get("full_url")) == str(full_url):
                    return URLModel(**existing_url)
                else:
                    # Hash collision detected! Generate a new short_id by salting it
                    short_id = generate_short_id(str(full_url) + str(uuid.uuid4()))
            else:
                break
        
        url_data = URLModel(
            short_id=short_id,
            full_url=full_url,
        )

        data_for_db = url_data.model_dump(mode="json")
        
        await self.collection.insert_one(data_for_db)
        await self.redis.setex(short_id, REDIS_STORE_TIME, str(full_url))  # Cache in Redis
        
        return url_data
    
    async def get_full_url_by_short_id(self, short_id: str) -> str:
        # Check Redis cache first
        cached_url = await self.redis.get(short_id)
        if cached_url:
            return cached_url
        
        # If not in cache, fetch from MongoDB
        url_data = await self.collection.find_one({"short_id": short_id})
        if not url_data:
            raise HTTPException(status_code=404, detail="URL not found")
        
        full_url = str(url_data['full_url'])
        await self.redis.setex(short_id, REDIS_STORE_TIME, full_url)  # Cache in Redis
        
        return full_url
