from typing import Optional
from pydantic import BaseModel, HttpUrl



class UserOtpSend(BaseModel):
    phone: str


class UserOtpVerify(BaseModel):
    phone: str
    otp: str


class UserLoginPassword(BaseModel):
    phone: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    gender: Optional[str] = None
    dob: Optional[str] = None
    profile_pic_url: Optional[HttpUrl] = None
    user_type_id: Optional[int] = None
    community_id: Optional[int] = None


class UserDelete(BaseModel):
    inactive_reson:str


class UserPhoneOtpSend(BaseModel):
    user_id: int
    phone: str


class UserPhoneOtpVerify(BaseModel):
    user_id: int
    phone: str
    otp: str

class UserBlockedCreate(BaseModel):
    user_id: int
    user_id_blocked: int

class UserBlockedDelete(BaseModel):
    user_id: int
    user_id_blocked: int




