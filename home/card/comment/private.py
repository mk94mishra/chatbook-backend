from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

router = APIRouter(prefix='/v1/private', tags=["private-card-comment"])


# get card post single comment
@router.get("/card-comment/post/{post_id}", status_code=status.HTTP_200_OK)
async def card_comment_post(request:Request,post_id:int, limit: Optional[int] = 10, offset: Optional[int] = 0, order_by: Optional[str] = 'c.created_at desc'):

    logged_in_user = request.state.user_id

    try:
        async with in_transaction() as connection:
            sql = "select c.*, lcu.is_like from tbl_card_comment as c"

            liked_user_sql = " left join lateral (select lc.comment_id,lc.user_id,true as is_like from tbl_like_comment as lc where lc.user_id={logged_in_user}) as lcu on c.id=lcu.comment_id".format(logged_in_user=logged_in_user)

            sql = sql + liked_user_sql

            where = " where c.post_id={post_id}".format(post_id=post_id)

            orderby = " order by {order_by} limit {limit} offset {offset}".format(order_by=order_by, limit=limit,offset=offset)

            sql = sql + where + orderby
            print(sql)
            card_comment = await connection.execute_query(sql)
            return success_response(card_comment[1])
    except OperationalError:
        return error_response(code=400, message="something error!")


# get card-comment commented
@router.get("/card-comment/comment/{comment_id}", status_code=status.HTTP_200_OK)
async def card_post_commente_single(request:Request, comment_id:int):
    logged_in_user = request.state.user_id
    try:
        async with in_transaction() as connection:
            sql = "select c.*, lcu.is_like from tbl_card_comment as c"
            liked_user_sql = " left join lateral (select lc.comment_id,lc.user_id,true as is_like from tbl_like_comment as lc where lc.user_id={logged_in_user}) as lcu on c.id=lcu.comment_id".format(logged_in_user=logged_in_user)
            sql = sql + liked_user_sql
            where = " where c.id={comment_id}".format(comment_id=comment_id)

            sql = sql + where
            print(sql)
            card_comment = await connection.execute_query(sql)
            return success_response(card_comment[1])
    except OperationalError:
        return error_response(code=400, message="something error!")



