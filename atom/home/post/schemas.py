from typing import List, Optional

from pydantic import BaseModel

class PostCreate(BaseModel):
    user_id: int
    description: Optional[str] = None
    media_type: Optional[str] = None
    media_url: List[str] = []
    thumbnail_url: List[str] = []
    category_id: int




