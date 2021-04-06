from typing import Optional

from pydantic import BaseModel

class LikePostCreate(BaseModel):
    post_id: int
    user_id: int

class LikeCommentCreate(BaseModel):
    comment_id: int
    user_id: int



