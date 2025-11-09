from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.api.schemas import URLCreate, URLResponse, URLDelete
from app.services.url_service import (
    create_short_url,
    get_long_url_by_short_id,
    delete_url
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
    return RedirectResponse(url=long_url, status_code=307)

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