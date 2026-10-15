from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis
from app.models.mongo_models import URLModel
from fastapi import HTTPException
from app.utils.hash_generator import generate_short_id
import uuid

REDIS_STORE_TIME = 60 * 60 * 24

class URLService:
    def __init__(self, database: AsyncIOMotorDatabase, redis: Redis): 
        self.collection = database[URLModel.Settings.collection_name]
        self.redis = redis
    
    async def create_short_url(self, full_url: str) -> URLModel:
        short_id = generate_short_id(str(full_url))
        while True:
            existing_url = await self.collection.find_one({"short_id": short_id})
            if existing_url:
                if str(existing_url.get("full_url")) == str(full_url):
                    return URLModel(**existing_url)
                else:
                    # A different URL already owns this ID. Salting makes the new ID random rather than derived from the URL, so it can't be looked up again by re-hashing (see README limitations).
                    short_id = generate_short_id(str(full_url) + str(uuid.uuid4()))
            else:
                break
        
        url_data = URLModel(
            short_id=short_id,
            full_url=full_url,
        )

        data_for_db = url_data.model_dump(mode="json")
        
        await self.collection.insert_one(data_for_db)
        # Cache on write too: new links are usually opened soon after they're created
        await self.redis.setex(short_id, REDIS_STORE_TIME, str(full_url))
        
        return url_data
    
    async def get_full_url_by_short_id(self, short_id: str) -> str:
        cached_url = await self.redis.get(short_id)
        if cached_url:
            return cached_url
        
        url_data = await self.collection.find_one({"short_id": short_id})
        if not url_data:
            raise HTTPException(status_code=404, detail="URL not found")
        
        full_url = str(url_data['full_url'])
        await self.redis.setex(short_id, REDIS_STORE_TIME, full_url)
        
        return full_url
