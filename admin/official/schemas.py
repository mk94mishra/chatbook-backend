from typing import Optional

from pydantic import BaseModel

class OfficialCreate(BaseModel):
    type:str
    title: str
    description: Optional[str] = None
    url: Optional[str] = None





