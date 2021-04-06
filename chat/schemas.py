from typing import Optional
from pydantic import BaseModel


class ChatCreate(BaseModel):
    sender_id:int
    receiver_id:int
    msg:str 


class ChatUpdate(BaseModel):
    sender_id:int
    receiver_id:int

class ChatRequestConfirm(BaseModel):
    request_id:int
    sender_id:int
    receiver_id:int
    is_activated: bool

class ChatRequestCheck(BaseModel):
    sender_id:int
    receiver_id:int