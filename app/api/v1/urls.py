from fastapi import APIRouter, HTTPException, Depends
from app.core.db import db
from app.api.v1.types import URLCreate, URLResponse
from app.services.url_service import URLService
from fastapi.responses import RedirectResponse as StarletteRedirectResponse # Rename to avoid confusion

router = APIRouter()

BASE_URL = "http://localhost:8000"  # Change to your domain

def get_url_service():
    return URLService(database=db.db, redis=db.redis)

@router.post("/shorten", response_model=URLResponse)
async def create_short_url(url: URLCreate, service: URLService = Depends(get_url_service)):
    """
    Docstring for create_short_url
    
    :param url: Description
    :type url: URLCreate
    """
    url = await service.create_short_url(url.full_url) # , url.user_id
                                         
    return URLResponse(
        short_id=url.short_id,
        full_url=str(url.full_url),
        created_at=url.created_at,
        short_url=f"{BASE_URL}/{url.short_id}"
    )

@router.get("/{short_id}", response_class=StarletteRedirectResponse)
async def redirect_to_full(short_id: str, service: URLService = Depends(get_url_service)):
    """
    Docstring for redirect_to_full
    
    :param short_id: Description
    :type short_id: str
    """
    full_url = await service.get_full_url_by_short_id(short_id)
    return StarletteRedirectResponse(url=full_url, status_code=301)