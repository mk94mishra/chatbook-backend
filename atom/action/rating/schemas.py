from typing import Optional

from pydantic import BaseModel

class RatingCreate(BaseModel):
    user_id: int
    user_rated_id: int
    rating: float

class RatingUpdate(BaseModel):
    rating: float

class RatingDelete(BaseModel):
    user_id: int
    user_rated_id: int




