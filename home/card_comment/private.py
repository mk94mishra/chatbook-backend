from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from user.models import User

router = APIRouter(prefix='/v1/private/card-comment', tags=["private-card-comment"])


# get card-comment all
@router.get("/post/{post_id}", status_code=status.HTTP_200_OK)
async def card_comment_all(request:Request,post_id:int,limit: Optional[int] = 10, offset: Optional[int] = 0):
    
    sql = "select * from tbl_card_comment"
    where = " where post_id={post_id}".format(post_id=post_id)
    orderby = " order by created_at desc limit {limit} offset {offset}".format(limit=limit,offset=offset)
    sql = sql + where + orderby
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(card_post[1])
    except OperationalError:
        return error_response(code=400, message="something error!")



# get card-comment user
@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def card_comment_user(request:Request,user_id:int,limit: Optional[int] = 10, offset: Optional[int] = 0):
    # self user check
    if int(user_id) != int(request.state.user_id):
        return error_response(code=401, message="you don't have permission!")
    
    sql = "select * from tbl_card_comment"
    where = " where user_id={user_id}".format(user_id=user_id)
    orderby = " order by created_at desc limit {limit} offset {offset}".format(limit=limit,offset=offset)
    sql = sql + where + orderby
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(card_post[1])
    except OperationalError:
        return error_response(code=400, message="something error!")


   