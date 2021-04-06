from typing import Optional
from pydantic import BaseModel


class ChatCreate(BaseModel):
    sender_id:int
    receiver_id:int
    msg:str 


class ChatUpdate(BaseModel):
    sender_id:int
    receiver_id:int