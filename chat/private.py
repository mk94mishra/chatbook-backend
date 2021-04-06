from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, Header, HTTPException
import hashlib
import datetime
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction

from system.settings import settings
from common.response import error_response, success_response

from chat.models import Chat, ChatRequest
from chat.schemas import ChatCreate, ChatUpdate, ChatRequestConfirm, ChatRequestCheck


router = APIRouter(prefix='/v1/private', tags=["chat"])


# chat request check
@router.post("/chat/request-check", status_code=status.HTTP_200_OK)
async def chat_request_check(request: Request, payload: ChatRequestCheck):
    data = deepcopy(payload.dict())
    # self user check
    if int(data['sender_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    if data['sender_id'] < data['receiver_id']:
        data['group_id'] = "{sender_id}-{receiver_id}".format(sender_id=data['sender_id'],receiver_id=data['receiver_id'])
    else:
        data['group_id'] = "{receiver_id}-{sender_id}".format(receiver_id=data['receiver_id'], sender_id=data['sender_id'])
    
    chat_request_exist = await ChatRequest.filter(group_id=data['group_id'], is_activated=True).exists()
    if chat_request_exist:
        response  = True
    else:
        response  = False
    return success_response(response)


# chat request create
@router.post("/chat/request-create", status_code=status.HTTP_200_OK)
async def chat_request_create(request: Request, payload: ChatCreate):
    data = deepcopy(payload.dict())
    # self user check
    if int(data['sender_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data = {k: v for k, v in payload.dict().items() if v is not None}
    # create group id
    if data['sender_id'] < data['receiver_id']:
        data['group_id'] = "{sender_id}-{receiver_id}".format(sender_id=data['sender_id'],receiver_id=data['receiver_id'])
    else:
        data['group_id'] = "{receiver_id}-{sender_id}".format(receiver_id=data['receiver_id'], sender_id=data['sender_id'])

    return success_response(await ChatRequest.create(**data))



# chat request pending list
@router.get("/chat/request-pending/user/{user_id}", status_code=status.HTTP_200_OK)
async def chat_request_pending(request: Request, user_id: int):
    return success_response(await ChatRequest.filter(user_id=user_id, is_activated=None)).order_by('-created_at')


# chat request true false
@router.post("/chat/request-confirm", status_code=status.HTTP_200_OK)
async def chat_request_confirm(request: Request, payload: ChatRequestConfirm):
    data = deepcopy(payload.dict())
    # self user check
    if int(data['receiver_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    # create group id
    if data['sender_id'] < data['receiver_id']:
        data['group_id'] = "{sender_id}-{receiver_id}".format(sender_id=data['sender_id'],receiver_id=data['receiver_id'])
    else:
        data['group_id'] = "{receiver_id}-{sender_id}".format(receiver_id=data['receiver_id'], sender_id=data['sender_id'])

    try:
        async with in_transaction() as connection:
            if data['is_activated'] == False:
                chat_request_exist = await ChatRequest.filter(group_id=data['group_id'], is_activated=True).exists()
                if chat_request_exist:
                    return success_response({"msg":"chat request is accepted! you can't reject"})
                
                activate_false_sql = "update tbl_chat_request set is_activated=False where id='{request_id}' and group_id='{group_id} ".format(request_id=data['request_id'], group_id=data['group_id'])
                await connection.execute_query(activate_false_sql)
                return success_response({"msg":"chat request rejected"})

            activate_true_sql = "update tbl_chat_request set is_activated=True where group_id='{group_id}' ".format(group_id=data['group_id'])
            await connection.execute_query(activate_true_sql)

            chat_request_msg = await ChatRequest.filter(group_id=data['group_id']).order_by('created_at')
            
            sql = """insert into tbl_chat_msg (group_id,sender_id, receiver_id, is_seen_min, is_seen_max, is_deleted_min, is_deleted_max, msg) values """

            sql_values = ""
            i = 1
            for chat_msg in chat_request_msg:
                if i > 1:
                    sql_values = sql_values + ","
                i = i + 1   
                sql_values = sql_values + "('{group_id}','{sender_id}', '{receiver_id}', '{is_seen_min}', '{is_seen_max}', '{is_deleted_min}', '{is_deleted_max}', '{msg}')".format(group_id=chat_msg.group_id,sender_id=chat_msg.sender_id, receiver_id=chat_msg.receiver_id, is_seen_min='True', is_seen_max='True', is_deleted_min='False', is_deleted_max='False', msg=chat_msg.msg)
            sql = sql + sql_values
            await connection.execute_query(sql)
            return success_response({"msg": "data created!"})
    except OperationalError:
        return error_response(code=400, message="something error!")


# ------------------------------------------------------------------------------------------


# chat
@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat_create(request: Request, payload: ChatCreate):
    data = deepcopy(payload.dict())
    # self user check
    if int(data['sender_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data = {k: v for k, v in payload.dict().items() if v is not None}
    # create group id
    if data['sender_id'] < data['receiver_id']:
        data['group_id'] = "{sender_id}-{receiver_id}".format(sender_id=data['sender_id'],receiver_id=data['receiver_id'])
        data['is_seen_min'] = True
    else:
        data['group_id'] = "{receiver_id}-{sender_id}".format(receiver_id=data['receiver_id'], sender_id=data['sender_id'])
        data['is_seen_max'] = True

    chat_request_exist = await ChatRequest.filter(group_id=data['group_id'], is_activated=False).exists()
    if chat_request_exist:
        return success_response({"msg":"you can't send!"})

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

