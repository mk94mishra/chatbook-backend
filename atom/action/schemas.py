from typing import Optional

from pydantic import BaseModel

class ActionCreate(BaseModel):
    user_id: int
    post_id: Optional[int]= None
    comment_id: Optional[int]= None
    description: Optional[str]= None
    media_url: Optional[str]= None
    user_id_blocked_id: Optional[int]= None
    user_id_rated_id: Optional[int]= None
    rating: Optional[float]= None





