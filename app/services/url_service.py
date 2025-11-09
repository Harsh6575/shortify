from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.postgres_models import URL
from app.utils.hash_generator import generate_short_id
from app.utils.redis_cache import (
    get_long_url,
    set_long_url,
    delete_short_url,
    refresh_ttl
)
from fastapi import HTTPException
from typing import Optional

async def create_short_url(long_url: str, db: AsyncSession, user_id: Optional[int] = None) -> URL:
    """
    Create a short URL.
    1. Generate hash-based short_id
    2. Check if exists in DB (handle collision)
    3. Save to PostgreSQL
    4. Cache in Redis
    """
    short_id = generate_short_id(long_url, user_id)
    
    # Check if short_id already exists
    result = await db.execute(select(URL).where(URL.short_id == short_id))
    existing = result.scalar_one_or_none()
    
    if existing:
        # If same URL, return existing
        if existing.long_url == long_url:
            return existing
        
        # Collision: append timestamp for uniqueness
        import time
        short_id = generate_short_id(f"{long_url}:{int(time.time())}", user_id)
    
    # Create new URL record
    new_url = URL(short_id=short_id, long_url=long_url)
    db.add(new_url)
    await db.commit()
    await db.refresh(new_url)
    
    # Cache in Redis
    await set_long_url(short_id, long_url)
    
    return new_url

async def get_long_url_by_short_id(short_id: str, db: AsyncSession) -> str:
    """
    Get long URL by short_id.
    1. Check Redis cache first
    2. If not in cache, query PostgreSQL
    3. Cache the result
    4. Refresh TTL if found in cache
    """
    # Try Redis first
    cached_url = await get_long_url(short_id)
    if cached_url:
        # Refresh TTL since URL is being used
        await refresh_ttl(short_id)
        return cached_url
    
    # Query PostgreSQL
    result = await db.execute(select(URL).where(URL.short_id == short_id))
    url = result.scalar_one_or_none()
    
    if not url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    # Cache for future requests
    await set_long_url(short_id, url.long_url)
    
    return url.long_url

async def delete_url(short_id: str, db: AsyncSession) -> bool:
    """
    Delete a short URL.
    1. Delete from PostgreSQL
    2. Delete from Redis cache
    """
    # Delete from database
    result = await db.execute(delete(URL).where(URL.short_id == short_id))
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    # Delete from Redis
    await delete_short_url(short_id)
    
    return True