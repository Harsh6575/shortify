from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.core.db import db
from app.api.v1.types import URLCreate, URLResponse
from app.services.url_service import URLService

router = APIRouter()
# Mounted at the root rather than under /api/v1, so short links stay short
redirect_router = APIRouter()

def get_url_service():
    return URLService(database=db.db, redis=db.redis)

@router.post("/shorten", response_model=URLResponse)
async def create_short_url(url: URLCreate, service: URLService = Depends(get_url_service)):
    """Shorten a URL. Shortening the same URL again returns the existing short ID."""
    url = await service.create_short_url(url.full_url)

    return URLResponse(
        short_id=url.short_id,
        full_url=str(url.full_url),
        created_at=url.created_at,
        short_url=f"{settings.BASE_URL}/{url.short_id}"
    )

@redirect_router.get("/{short_id}", response_class=RedirectResponse)
async def redirect_to_full(short_id: str, service: URLService = Depends(get_url_service)):
    """Redirect to the original URL, or 404 if the short ID doesn't exist."""
    full_url = await service.get_full_url_by_short_id(short_id)
    return RedirectResponse(url=full_url, status_code=301)