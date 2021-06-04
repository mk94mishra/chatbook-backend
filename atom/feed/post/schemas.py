from typing import List, Optional

from pydantic import BaseModel

class Feed(BaseModel):
    distance:  Optional[int] = None 
    gender:  Optional[str] = None 

    description: Optional[str] = None
    category_id: Optional[int] = None
    designation_id: Optional[int] = None
    community_id: Optional[int] = None

    limit: Optional[int] = 10
    offset: Optional[int] = 0





