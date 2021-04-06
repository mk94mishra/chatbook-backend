from typing import Optional

from pydantic import BaseModel

class FaqCreate(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None





