from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from user.models import User

from home.card.query_function import card_post_private, card_post_private_response

router = APIRouter(prefix='/v1/private/card-post', tags=["private-card-post"])


# get card-post all
@router.get("/fresh", status_code=status.HTTP_200_OK)
async def card_post_fresh(request:Request, limit: Optional[int] = 10, offset: Optional[int] = 0):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    user_data = {
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long,
        "logged_in_community_id": user.community_id,
    }

    try:
        async with in_transaction() as connection:
            sql = card_post_private(**user_data)
            
            orderby = " order by created_at desc nulls last limit {limit} offset {offset}".format( limit=limit,offset=offset)
            sql = sql + orderby

            card_post = await connection.execute_query(sql)
            return success_response(card_post_private_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")

