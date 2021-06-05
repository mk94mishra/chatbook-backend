from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from atom.user.models import User

from atom.feed.post.schemas import Feed
from atom.helper.helper import post_master_public_response

router = APIRouter(prefix='/v1/public/feed-post', tags=["public-feed-post"])


# get feed-post all
@router.get("", status_code=status.HTTP_200_OK)
async def post_master_all(request:Request,limit: Optional[int] = 10, offset: Optional[int] = 0):
    sql = " select * from tbl_post_master"
    orderby = " order by count_like desc nulls last limit {limit} offset {offset}".format(limit=limit,offset=offset)

    sql = sql + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            post_master = await connection.execute_query(sql)
            return success_response(post_master_public_response(post_master[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")



# get feed-post single
@router.get("/post/{post_id}", status_code=status.HTTP_200_OK)
async def post_master_single(request:Request,post_id: int):
    sql = "select * from tbl_post_master"
    where = " where id = {post_id}".format(post_id=post_id)
    
    sql = sql + where
    try:
        async with in_transaction() as connection:
            post_master = await connection.execute_query(sql)
            return success_response(post_master_public_response(post_master[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")


# get feed-post single user
@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def post_master_user(request:Request,user_id: int):
    sql = "select * from tbl_post_master"
    where = " where user_id = {user_id}".format(user_id=user_id)
    
    sql = sql + where
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(post_master_public_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")

