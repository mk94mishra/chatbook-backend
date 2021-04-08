from typing import Optional

from pydantic import BaseModel

class ActionCreate(BaseModel):
    post_id: int
    user_id: int
    description: Optional[str]= None
    media_url: Optional[str]= None
    method: str





