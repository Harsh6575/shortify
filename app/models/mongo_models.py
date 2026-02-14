from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime, timezone
from typing import Optional

class URLModel(BaseModel):
    short_id: str = Field(..., unique=True)
    full_url: HttpUrl
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None

    class Settings:
        collection_name = "urls"