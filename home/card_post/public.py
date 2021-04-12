from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from user.models import User

from home.card_post.schemas import Feed
from admin.helper.helper.py import card_post_public_response

router = APIRouter(prefix='/v1/public/card-post', tags=["public-card-post"])


# get card-post all
@router.get("", status_code=status.HTTP_200_OK)
async def card_post_all(request:Request,limit: Optional[int] = 10, offset: Optional[int] = 0):
    sql = " select * from tbl_card_post"
    orderby = " order by count_like desc nulls last limit {limit} offset {offset}".format(limit=data['limit'],offset=data['offset'])

    sql = sql + orderby
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(card_post_public_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")



# get card-post single
@router.get("/post/{post_id}", status_code=status.HTTP_200_OK)
async def card_post_all(request:Request,post_id: str):
    sql = "select * from tbl_card_post"
    where = " where id = {post_id}".format(post_id=post_id)
    
    sql = sql + where
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(card_post_public_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")

