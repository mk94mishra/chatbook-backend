from typing import Optional

from pydantic import BaseModel

class RatingCreate(BaseModel):
    user_id:int
    user_id_rated_id:int
    rating: float





