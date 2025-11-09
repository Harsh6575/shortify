from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.api.schemas import URLCreate, URLResponse, URLDelete, URLListResponse
from app.services.url_service import (
    create_short_url,
    get_long_url_by_short_id,
    delete_url,
    get_recent_urls
)

router = APIRouter(prefix="/api", tags=["urls"])

BASE_URL = "http://localhost:8000"  # Change to your domain

@router.post("/shorten", response_model=URLResponse)
async def shorten_url(
    url_data: URLCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a short URL.
    """
    url = await create_short_url(
        long_url=str(url_data.long_url),
        db=db,
        user_id=url_data.user_id
    )
    
    return URLResponse(
        short_id=url.short_id,
        long_url=url.long_url,
        created_at=url.created_at,
        short_url=f"{BASE_URL}/{url.short_id}"
    )

@router.get("/{short_id}")
async def redirect_to_long_url(
    short_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Redirect to the original long URL.
    """
    long_url = await get_long_url_by_short_id(short_id, db)
    return RedirectResponse(url=long_url, status_code=301)

@router.delete("/urls/{short_id}")
async def delete_short_url(
    short_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a short URL.
    """
    await delete_url(short_id, db)
    return {"message": f"Short URL '{short_id}' deleted successfully"}

@router.get("/urls/recent", response_model=URLListResponse)
async def get_recent_shortened_urls(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get last N shortened URLs (for development).
    Default: 10
    """
    urls = await get_recent_urls(db, limit)
    
    url_responses = [
        URLResponse(
            short_id=url.short_id,
            long_url=url.long_url,
            created_at=url.created_at,
            short_url=f"{BASE_URL}/{url.short_id}"
        )
        for url in urls
    ]
    
    return URLListResponse(
        urls=url_responses,
        total=len(url_responses)
    )