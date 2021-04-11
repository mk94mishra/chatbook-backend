from typing import List, Optional

from pydantic import BaseModel

class Feed(BaseModel):
    feed: str # fresh
    distance:  Optional[int] = None 
    limit: Optional[int] = 10
    offset: Optional[int] = 0





