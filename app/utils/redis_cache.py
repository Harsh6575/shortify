from app.core.db import redis_client
from typing import Optional

CACHE_TTL = 60 * 60 * 24 * 7  # 7 days in seconds

async def get_full_url(short_id: str) -> Optional[str]:
    """
    Get long URL from Redis cache.
    Returns None if not found.
    """
    full_url = await redis_client.get(f"short:{short_id}")
    if full_url:
        return full_url.decode('utf-8')
    return None

async def set_full_url(short_id: str, full_url: str) -> None:
    """
    Cache short_id -> full_url mapping in Redis.
    TTL: 7 days
    """
    await redis_client.setex(
        f"short:{short_id}",
        CACHE_TTL,
        full_url
    )

async def delete_short_url(short_id: str) -> None:
    """
    Remove short URL from Redis cache.
    """
    await redis_client.delete(f"short:{short_id}")

async def refresh_ttl(short_id: str) -> None:
    """
    Reset TTL to 7 days when URL is accessed.
    """
    await redis_client.expire(f"short:{short_id}", CACHE_TTL)