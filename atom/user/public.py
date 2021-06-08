from copy import deepcopy
from fastapi import APIRouter, Request, status, Header, HTTPException
from random_username.generate import generate_username 
import hashlib
from time import time
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction

from common.token import token_create
from common.validation import form_validation
from common.response import error_response, success_response
from common.otp import generate_and_send_otp, verify_generated_otp

from common.validation import form_validation

from atom.user.models import User
from atom.user.schemas import UserOtpSend, UserUpdate, UserOtpVerify, UserLoginPassword



router = APIRouter(prefix='/v1/public/user', tags=["public-user"])


# enter user
@router.post("/login-phone-otp/send-otp", status_code=status.HTTP_201_CREATED)
async def user_otp_send(request: Request, payload: UserOtpSend):
    data = deepcopy(payload.dict())
    data = {k: v for k, v in payload.dict().items() if v is not None}

    ok, err = form_validation('mobile', data['phone'])
    if err:
        return error_response(code=400, message=err)

    user = await User.get(phone=data['phone']).exists()
    if not user:
        # create random username
        random_username = generate_username(1)
        data['name'] = random_username[0]
        await User.create(**data)
    
    ok, err = generate_and_send_otp(data['phone'])
    # ok, if sms sent
    if ok:
        return success_response({"msg":"otp sent", "next":"otp-verify"})
    # err, if found error
    if err:
        return  error_response(code=400, message="otp not sent")


        
# otp verify
@router.post("/login-phone-otp/verify-otp", status_code=status.HTTP_200_OK)
async def user_otp_verify(request: Request, payload: UserOtpVerify):
    data = deepcopy(payload.dict())
    data = {k: v for k, v in payload.dict().items() if v is not None}
    
    ok, err = form_validation('mobile', data['phone'])
    if err:
        return error_response(code=400, message=err)
    # try, user phone existance
    try:
        user = await User.get(phone=data['phone'])
        # true, when verify otp 
        if verify_generated_otp(data['phone'], data['otp']):

            if user.is_phone_verified == False:
                # update , is phone verified true
                await User(id=user.id, is_phone_verified=True).save(update_fields=['is_phone_verified'])
            
            # create token value
            claims = {
                'sub': user.id
            }
            # check community & user type
            if (not user.community_id) or (not user.designation_id) or (not user.gender):
                return success_response({"token": token_create(claims),"user_id": user.id, "next": "update-profile"})  
            # create token and send user to update profile
            return success_response({"token": token_create(claims),"user_id": user.id, "next": "home"})
        return error_response(code=403, message="otp not verified!")

    # user not exist
    except DoesNotExist:
        return error_response(code=404, message="phone number not exist!")


# password login
@router.post("/login-phone-password", status_code=status.HTTP_200_OK)
async def login_phone_password(request: Request, payload: UserLoginPassword):
    data = deepcopy(payload.dict())
    data = {k: v for k, v in payload.dict().items() if v is not None}

    ok, err = form_validation('mobile', data['phone'])
    if err:
        return error_response(code=400, message=err)

    # try, user phone existance
    try:
        user = await User.get(phone=data['phone'])

        if user.password != hashlib.md5(data['password'].encode()).hexdigest():
            return error_response(code=404, message="wrong password!")

        # create token value
        claims = {
            'sub': user.id
        }
        # check community & user type
        if (not user.community_id) or (not user.designation_id) or (not user.gender):
            return success_response({"token": token_create(claims),"user_id": user.id, "next": "update-profile"})
        return success_response({"token": token_create(claims), "user_id": user.id, "next": "home"})

    # when phone number not exist
    except DoesNotExist:
        return error_response(code=404, message="phone number not exist!")


#  user check
@router.get("/{user_id}/user-check", status_code=status.HTTP_200_OK)
async def user_check(request: Request, user_id:int):
    user = await User.get(id=user_id)
    return success_response({"is_active":user.is_active})


