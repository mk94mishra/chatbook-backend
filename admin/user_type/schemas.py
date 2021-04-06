from typing import Optional

from pydantic import BaseModel



class UserTypeCreate(BaseModel):
    name: str


