from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from atom.user.models import User

from atom.helper.helper import comment_master_token

router = APIRouter(prefix='/v1/token/feed-comment', tags=["token-feed-comment"])


# get feed-comment all
@router.get("/post/{post_id}", status_code=status.HTTP_200_OK)
async def comment_master_all(request:Request,post_id: int, limit: Optional[int]=10, offset: Optional[int]=0):
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    user_data = {
        "logged_in_user_id": logged_in_user_id,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }
    sql = comment_master_token(**user_data)
    where = " and c.post_id={post_id}".format(post_id=post_id)
    orderby = " order by acl.created_at desc nulls last limit {limit} offset {offset}".format(limit=limit,offset=offset)

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            comment_master = await connection.execute_query(sql)
            return success_response(comment_master[1])
    except OperationalError:
        return error_response(code=400, message="something error!")

        
# get feed-comment user
@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def comment_master_user(request:Request,user_id: int, limit: Optional[int]=10, offset: Optional[int]=0):
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    user_data = {
        "logged_in_user_id": logged_in_user_id,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }
    sql = comment_master_token(**user_data)
    where = " and c.user_id={user_id}".format(user_id=user_id)
    orderby = " order by acl.created_at desc nulls last limit {limit} offset {offset}".format(limit=limit,offset=offset)

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            comment_master = await connection.execute_query(sql)
            return success_response(comment_master[1])
    except OperationalError:
        return error_response(code=400, message="something error!")


# get feed-comment my comment
@router.get("/my-comment", status_code=status.HTTP_200_OK)
async def comment_master_my_comment(request:Request,limit: Optional[int]=10, offset: Optional[int]=0):
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    user_data = {
        "logged_in_user_id": logged_in_user_id,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }
    sql = comment_master_token(**user_data)
    where = " and c.user_id={logged_in_user_id}".format(logged_in_user_id=logged_in_user_id)
    orderby = " order by acl.created_at desc nulls last limit {limit} offset {offset}".format(limit=limit,offset=offset)

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            comment_master = await connection.execute_query(sql)
            return success_response(comment_master[1])
    except OperationalError:
        return error_response(code=400, message="something error!")
