from typing import Optional
from pydantic import BaseModel, HttpUrl


class OptionCreate(BaseModel):
    name: str
    type: str 
    icon_url1: Optional[HttpUrl] = None
    icon_url2: Optional[HttpUrl] = None

