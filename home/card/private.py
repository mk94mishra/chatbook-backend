from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from user.models import User

from home.card.schemas import Feed
from home.card.query_function import card_post_private, card_post_private_response

router = APIRouter(prefix='/v1/private/card-post', tags=["private-card-post"])


# get card-post all
@router.post("", status_code=status.HTTP_200_OK)
async def card_post_all(request:Request,payload: Feed):
    data = deepcopy(payload.dict())
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    user_data = {
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long,
        "logged_in_community_id": user.community_id
    }
    sql = card_post_private(**user_data)
    where = ""
    if data['distance']:
        where = " and distance <= {distance}".format(distance=data['distance'])
    if data['type'] == 'fresh':
        order_by = "created_at desc"
    if data['type'] == 'most-liked':
        order_by = "count_like desc"
    if data['type'] == 'trending':
        where = where + " and ageing <= 1"
        order_by = "count_like desc"

    orderby = " order by {order_by} nulls last limit {limit} offset {offset}".format(order_by=order_by,limit=data['limit'],offset=data['offset'])

    sql = sql + where + orderby
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(card_post_private_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")

