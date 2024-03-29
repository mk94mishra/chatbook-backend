from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, Header, HTTPException
from random_username.generate import generate_username 
import hashlib
import datetime
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction

from common.validation import form_validation
from common.response import error_response, success_response
from common.otp import generate_and_send_otp, verify_generated_otp

from atom.user.models import User
from atom.user.schemas import UserOtpSend, UserUpdate, UserOtpVerify, UserLoginPassword, UserPhoneOtpVerify, UserPhoneOtpSend,UserDelete

router = APIRouter(prefix='/v1/token/user', tags=["user"])


# update user profile
@router.put("/{user_id}", status_code=status.HTTP_200_OK)
async def user_update(request: Request, user_id:int, payload: UserUpdate):
    # self user check
    if int(user_id) != int(request.state.user_id):
        return error_response(code=401, message="you don't have permission!")

    data = deepcopy(payload.dict())

    user = await User.get(id=user_id)

    if (user.is_deleted == True) or (user.is_active == False):
        return error_response(code=401, message="user is permanently deleted or deacticated!")

    ok, err = form_validation('gender', data['gender'])
    if err:
        return error_response(code=400, message=err)

    ok, err = form_validation('date', data['dob'])
    if err:
        return error_response(code=400, message=err)

    ok, err = form_validation('password', data['password'])
    if err:
        return error_response(code=400, message=err)
    
    if data['password']:
        password = data['password']
        data['password'] = hashlib.md5(password.encode()).hexdigest()
    
    data['updated_by'] = request.state.user_id
    
    data = {k: v for k, v in data.items() if v is not None}
    # update data
    await User(id=user_id, **data).save(update_fields=data.keys())
    return success_response({"msg": "data updated!"})


# get user
@router.get("/my-profile", status_code=status.HTTP_200_OK)
async def user_my_profile(request: Request):
    user_id = request.state.user_id

    try:
        async with in_transaction() as connection:
            sql = """select
                u.id as id, u.username, u.phone, 
                case when u.password notnull then true else false end as is_password,
                u.profile_pic_url,u.gender,u.rating,u.dob,u.community_id, u.designation_id,
                od.name as designation_name,
                oc.name as community_name
                from tbl_user as u
                left join tbl_option as od on u.designation_id=od.id
                left join tbl_option as oc on u.community_id=oc.id
                """

            filter = " where u.is_active = 'true' and u.id={user_id}".format(user_id=user_id)
            sql = sql + filter

            user = await connection.execute_query(sql)
         
            return success_response(user[1])
    except OperationalError:
        return error_response(code=400, message="something error!")


# delete user
@router.post("/{user_id}/delete", status_code=status.HTTP_200_OK)
async def user_delete(request: Request, user_id:int, payload: UserDelete):
    data = deepcopy(payload.dict())

    # self user check
    if int(user_id) != int(request.state.user_id):
        return error_response(code=401, message="you don't have permission!")
    
    try:
        user = await User.get(id=user_id)
        user_phone = user.phone
        if (user.is_deleted == True) or (user.is_active == False):
            return error_response(code=401, message="user is permanently deleted or deactivated!")
        
        data = dict()
        data['phone'] = str(user_phone) +","+ str(datetime.datetime.now())
        data['updated_by'] = request.state.user_id
        data['is_active'] = False
        data['is_deleted'] = True
        data = {k: v for k, v in data.items() if v is not None}
        # update data
        await User(id=user_id, **data).save(update_fields=data.keys())

        async with in_transaction() as connection:
            sql = "delete from tbl_block where user_id={user_id}".format(user_id=user_id)
            await connection.execute_query(sql)
            sql = "delete from tbl_like_post where user_id={user_id}".format(user_id=user_id)
            await connection.execute_query(sql)
            sql = "delete from tbl_like_comment where user_id={user_id}".format(user_id=user_id)
            await connection.execute_query(sql)
            sql = "delete from tbl_rating where user_id={user_id}".format(user_id=user_id)
            await connection.execute_query(sql)
            sql = "delete from tbl_comment where user_id={user_id}".format(user_id=user_id)
            await connection.execute_query(sql)

            sql = "update tbl_post set is_active=False, updated_by={user_id}, remark='by user' where user_id={user_id} and is_active=True".format(user_id=user_id)
            await connection.execute_query(sql)

            return success_response({"msg": "data deleted!"})
    except OperationalError:
        return error_response(code=400, message="something error!")
    
    

# phone otp send
@router.post("/phone-update/otp-send", status_code=status.HTTP_201_CREATED)
async def user_phone_otp_send(request: Request, payload: UserPhoneOtpSend):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=401, message="you don't have permission!")
        
    data = {k: v for k, v in payload.dict().items() if v is not None}
    ok, err = form_validation('mobile', data['phone'])
    if err:
        return error_response(code=400, message=err)

    ok, err = generate_and_send_otp(data['phone'])
    # ok, if sms sent
    if ok:
        return success_response({"msg":"otp sent", "next":"phone-otp-verify"})
    # err, if found error
    if err:
        return  error_response(code=400, message="otp not sent")


# phone otp verify
@router.put("/phone-update/otp-verify", status_code=status.HTTP_200_OK)
async def user_phone_otp_verify(request: Request, payload: UserPhoneOtpVerify):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=401, message="you don't have permission!")

    data = {k: v for k, v in payload.dict().items() if v is not None}

    user = await User.get(id=data['user_id'])
    if user.phone == data['phone']:
        return error_response(code=400, message="mobile number already exist!")

    if verify_generated_otp(data['phone'], data['otp']):

        new_phone = data['phone']
        await User(id=data['user_id'], phone=new_phone).save(update_fields=['phone'])
            
        return success_response({"msg":"phone number updated!"})
    return  error_response(code=400, message="invalide otp!")
    

# get user
@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def user_read(request: Request, user_id:int):
   
    try:
        async with in_transaction() as connection:
            sql = """select u.id as id, u.username, 
                u.profile_pic_url,u.gender,u.rating,u.dob,u.community_id, u.community_name,
                ud.id as designation_id, ud.name as designation_name
                from (SELECT u.*,com.name as community_name
                from tbl_user as u
                left join tbl_option as com 
                on u.community_id = com.id) as u
                left join tbl_option as ud
                on u.designation_id=ud.id
                """

            filter = " where u.is_active = 'true' and u.id={user_id}".format(user_id=user_id)
            sql = sql + filter

            user = await connection.execute_query(sql)
         
            return success_response(user[1])
    except OperationalError:
        return error_response(code=400, message="something error!")
  