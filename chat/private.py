from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, Header, HTTPException
import hashlib
import datetime
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction

from system.settings import settings
from common.response import error_response, success_response

from chat.models import Chat
from chat.schemas import ChatCreate, ChatUpdate


router = APIRouter(prefix='/v1/private', tags=["chat"])


# chat
@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat_create(request: Request, payload: ChatCreate):
    data = deepcopy(payload.dict())
    # self user check
    if int(data['sender_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data = {k: v for k, v in payload.dict().items() if v is not None}

    if data['sender_id'] < data['receiver_id']:
        data['group_id'] = "{sender_id}-{receiver_id}".format(sender_id=data['sender_id'],receiver_id=data['receiver_id'])
        data['is_seen_min'] = True
    else:
        data['group_id'] = "{receiver_id}-{sender_id}".format(receiver_id=data['receiver_id'], sender_id=data['sender_id'])
        data['is_seen_max'] = True

    return success_response(await Chat.create(**data))



# chat get
@router.get("/chat/group/{group_id}", status_code=status.HTTP_200_OK)
async def chat_get(request: Request, group_id:str, limit: Optional[int] = 50, offset: Optional[int] = 0):
    
    group_id_user = group_id.split('-')

    # self user check
    if (int(group_id_user[0]) != int(request.state.user_id)) & (int(group_id_user[1]) != int(request.state.user_id)):
        return error_response(code=400, message="you don't have permision!")        

    try:
        async with in_transaction() as connection:

            if int(group_id_user[0]) == int(request.state.user_id):
                set_is_seen = "is_seen_min = True"
                check_is_deleted = "is_deleted_min = False"

            if int(group_id_user[1]) == int(request.state.user_id):
                set_is_seen = "is_seen_max = True"
                check_is_deleted = "is_deleted_max = False"

            update_sql = "update tbl_chat_msg set {set_is_seen} where group_id='{group_id}'".format(set_is_seen=set_is_seen, group_id=group_id)

            await connection.execute_query(update_sql)

            # get chat msg
            sql = "select * from tbl_chat_msg"
            where = " where group_id='{group_id}' and {check_is_deleted}".format(group_id=group_id, check_is_deleted=check_is_deleted)
            orderby = " order by created_at desc limit {limit} offset {offset}".format(limit=limit,offset=offset)

            sql = sql + where + orderby
            print(sql)
            chat = await connection.execute_query(sql)
            return success_response(chat[1])
    except OperationalError:
        return error_response(code=400, message="something error!")



# chat delete
@router.delete("/chat/group/{group_id}", status_code=status.HTTP_200_OK)
async def chat_delete(request: Request, group_id:str, limit: Optional[int] = 50, offset: Optional[int] = 0):

    group_id_user = group_id.split('-')

    # self user check
    if (int(group_id_user[0]) != int(request.state.user_id)) & (int(group_id_user[1]) != int(request.state.user_id)):
        return error_response(code=400, message="you don't have permision!")        

    try:
        async with in_transaction() as connection:

            if int(group_id_user[0]) == int(request.state.user_id):
                set_is_deleted = "is_deleted_min = True"

            if int(group_id_user[1]) == int(request.state.user_id):
                set_is_deleted = "is_deleted_max = True"

            update_sql = "update tbl_chat_msg set {set_is_deleted} where group_id='{group_id}'".format(set_is_deleted=set_is_deleted, group_id=group_id)

            await connection.execute_query(update_sql)

            return success_response({"msg":"data deleted!"})
    except OperationalError:
        return error_response(code=400, message="something error!")



# chat user inbox
@router.get("/chat/user/{user_id}/inbox", status_code=status.HTTP_200_OK)
async def chat_user_inbox(request: Request, user_id:int, limit: Optional[int] = 50, offset: Optional[int] = 0):
    # self user check
    if int(user_id) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")
    
    try:
        async with in_transaction() as connection:
            sql = "select user_id_max as user_id, profile_pic_url_max as profile_pic_url, name_max as name, last_msg, is_seen_min as is_seen, created_at from tbl_chat_group where user_id_min={user_id} and is_deleted_min=False union select user_id_min as user_id,profile_pic_url_min as profile_pic_url, name_min as name, last_msg, is_seen_max as is_seen, created_at from tbl_chat_group where user_id_max={user_id} and is_deleted_max=False".format(user_id=user_id)

            orderby = " order by is_seen desc limit {limit} offset {offset}".format(limit=limit,offset=offset)

            sql = sql + orderby

            chat = await connection.execute_query(sql)
            return success_response(chat[1])
    except OperationalError:
        return error_response(code=400, message="something error!")

