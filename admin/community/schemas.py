from typing import Optional

from pydantic import BaseModel

class CommunityCreate(BaseModel):
    name: str

class CommunityUpdate(BaseModel):
    name: str



