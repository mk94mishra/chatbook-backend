from typing import List, Optional

from pydantic import BaseModel, HttpUrl

class CommentCreate(BaseModel):
    description: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[HttpUrl] = None
    post_id: int
    user_id: int

class CommentUpdate(BaseModel):
    description: Optional[str] = None
    media_url: Optional[HttpUrl] = None
    media_type: Optional[str] = None





