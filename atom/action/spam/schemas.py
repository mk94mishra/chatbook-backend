from typing import Optional

from pydantic import BaseModel

class SpamCreate(BaseModel):
    post_id: int
    user_id: int
    reason:str





