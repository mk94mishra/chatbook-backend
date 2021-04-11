from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from user.models import User

from home.card.query_function import card_post_private

router = APIRouter(prefix='/v1/private/card-post/base', tags=["private-card-post"])


# get card-post all
@router.get("/fresh", status_code=status.HTTP_200_OK)
async def card_post_all(request:Request, community_id: Optional[int] = 0,category_id: Optional[int] = 0, designation_id: Optional[int] = 0, description: Optional[str] = None, trending: Optional[bool] = None, limit: Optional[int] = 10, offset: Optional[int] = 0, order_by: Optional[str] = 'created_at desc'):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    logged_in_lat = user.lat
    logged_in_long = user.long
    try:
        async with in_transaction() as connection:
            sql = card_post_private(logged_in_user,logged_in_lat,logged_in_long)

            where = " where is_active=true and action_id_block isnull and action_id_block_me isnull"
            sql = sql + where
            card_post = await connection.execute_query(sql)
            card_post_list = list()
            for card_single in card_post[1]:
                media_data = None
                if card_single['media'] != None:
                    media_data = json.loads(card_single['media'])

                post = {
                    "post_id": card_single['id'],
                    "created_at": card_single['created_at'],
                    "description": card_single['description'],
                    "media": media_data,
                    "user_id": card_single['user_id'],
                    "username": card_single['username'],
                    "profile_pic_url": card_single['profile_pic_url'],
                    "designation_id": card_single['designation_id'],
                    "count_like": card_single['count_like'],
                    "count_comment": card_single['count_comment'],
                    "community_id": card_single['community_id'],
                    "category_id": card_single['category_id'],
                    "category_name": card_single['category_name'],
                    "distance":card_single['distance'],
                    "action_id_like":card_single['action_id_like'],
                    "action_id_bookmark":card_single['action_id_bookmark']
                }
                card_post_list.append(post)
            return success_response(card_post_list)
    except OperationalError:
        return error_response(code=400, message="something error!")

