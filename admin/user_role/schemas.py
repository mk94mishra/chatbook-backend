from typing import Optional

from pydantic import BaseModel

class UserRoleCreate(BaseModel):
    name: str



