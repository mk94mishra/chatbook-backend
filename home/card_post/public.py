from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from user.models import User

from home.card_post.schemas import Feed
from home.card_post.query_function import card_post_public_response

router = APIRouter(prefix='/v1/public/card-post', tags=["public-card-post"])


# get card-post all
@router.post("", status_code=status.HTTP_200_OK)
async def card_post_all(request:Request,payload: Feed):
    data = deepcopy(payload.dict())

    sql = " select * from tbl_card_post"
    where = "  where ageing <= 30"
    orderby = " order by count_like desc nulls last limit {limit} offset {offset}".format(limit=data['limit'],offset=data['offset'])

    sql = sql + where + orderby
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(card_post_public_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")

