from typing import Optional
from pydantic import BaseModel, HttpUrl


class OptionCreate(BaseModel):
    type: str 
    name: str
    icon_url_1: Optional[HttpUrl] = None
    icon_url_2: Optional[HttpUrl] = None

