from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional,List

class URLCreate(BaseModel):
    long_url: HttpUrl
    user_id: Optional[int] = None

class URLResponse(BaseModel):
    short_id: str
    long_url: str
    created_at: datetime
    short_url: str  # Full short URL for convenience

    class Config:
        from_attributes = True

class URLDelete(BaseModel):
    short_id: str

class RedirectResponse(BaseModel):
    long_url: str

class URLListResponse(BaseModel):
    urls: List[URLResponse]
    total: int