from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from user.models import User

from admin.helper.helper import card_comment_private

router = APIRouter(prefix='/v1/private/card-comment', tags=["private-card-comment"])


# get card-comment all
@router.get("/post/{post_id}", status_code=status.HTTP_200_OK)
async def card_comment_all(request:Request,post_id: int, limit: Optional[int]=10, offset: Optional[int]=0):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    user_data = {
        "logged_in_user": logged_in_user,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }
    sql = card_comment_private(**user_data)
    where = " and c.post_id={post_id}".format(post_id=post_id)
    orderby = " order by acl.created_at desc nulls last limit {limit} offset {offset}".format(limit=limit,offset=offset)

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            card_comment = await connection.execute_query(sql)
            return success_response(card_comment[1])
    except OperationalError:
        return error_response(code=400, message="something error!")



from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from user.models import User

from admin.helper.helper import card_comment_private

router = APIRouter(prefix='/v1/private/card-comment', tags=["private-card-comment"])


# get card-comment user
@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def card_comment_user(request:Request,user_id: int, limit: Optional[int]=10, offset: Optional[int]=0):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    user_data = {
        "logged_in_user": logged_in_user,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }
    sql = card_comment_private(**user_data)
    where = " and c.user_id={user_id}".format(user_id=user_id)
    orderby = " order by acl.created_at desc nulls last limit {limit} offset {offset}".format(limit=limit,offset=offset)

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            card_comment = await connection.execute_query(sql)
            return success_response(card_comment[1])
    except OperationalError:
        return error_response(code=400, message="something error!")


