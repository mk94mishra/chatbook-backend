from typing import Optional
from pydantic import BaseModel, HttpUrl


class OptionCreate(BaseModel):
    name: str
    type: str 
    icon1: Optional[HttpUrl] = None
    icon2: Optional[HttpUrl] = None

