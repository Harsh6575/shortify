from pydantic import BaseModel, HttpUrl
from datetime import datetime

class URLCreate(BaseModel):
    full_url: HttpUrl
    # user_id: Optional[int] = None

class URLResponse(BaseModel):
    short_id: str
    full_url: str
    created_at: datetime
    short_url: str  # Full short URL for convenience

    class Config:
        from_attributes = True