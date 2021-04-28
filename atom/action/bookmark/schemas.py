from typing import Optional

from pydantic import BaseModel

class BookmarkCreate(BaseModel):
    post_id: int
    user_id: int

class BookmarkDelete(BaseModel):
    post_id: int
    user_id: int




