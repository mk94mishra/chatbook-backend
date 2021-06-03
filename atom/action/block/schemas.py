from typing import Optional

from pydantic import BaseModel

class BlockCreate(BaseModel):
    user_id: int
    user_blocked_id: int

class BlockDelete(BaseModel):
    user_id: int
    user_blocked_id: int




