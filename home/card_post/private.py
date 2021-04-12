from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from user.models import User

from home.card_post.schemas import Feed
from home.card_post.query_function import card_post_private, card_post_private_response

router = APIRouter(prefix='/v1/private/card-post', tags=["private-card-post"])


# get card-post all
@router.post("", status_code=status.HTTP_200_OK)
async def card_post_all(request:Request,payload: Feed):
    data = deepcopy(payload.dict())
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    logged_in_community_id = user.community_id
    if user.community_id == None:
        return error_response(code=400, message="must be set community!")
    user_data = {
        "logged_in_user": logged_in_user,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }
    sql = card_post_private(**user_data)
    where = " and community_id={logged_in_community_id}".format(logged_in_community_id=logged_in_community_id)

    if data['distance']:
        where = where + " and distance <= {distance}".format(distance=data['distance'])
    order_by = ""
    if data['tab'] == 'fresh':
        order_by = "created_at desc"
    if data['tab'] == 'most-liked':
        order_by = "count_like desc"
    if data['tab'] == 'trending':
        where = where + " and ageing <= 1"
        order_by = "count_like desc"
    
    if data['type'] == 'home':
        pass

    if data['type'] == 'search':
        if not data['description']:
            return error_response(code=400, message="must be set search text!")
        where = where + " and description like %{description}%".format(description=data['description'])

    if data['type'] == 'category':
        if not data['category_id']:
            return error_response(code=400, message="must be set category_id!")
        where = where + " and category_id = {category_id}".format(category_id=data['category_id'])

    if data['type'] == 'designation':
        if not data['designation_id']:
            return error_response(code=400, message="must be set designation_id!")
        where = where + " and designation_id = {designation_id}".format(designation_id=data['designation_id'])

    orderby = " order by {order_by} nulls last limit {limit} offset {offset}".format(order_by=order_by,limit=data['limit'],offset=data['offset'])

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(card_post_private_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")



# get card-post user
@router.get("/type/{type_name}", status_code=status.HTTP_200_OK)
async def card_post_user(request:Request,type_name:str,limit:Optional[int] = 10, offset:Optional[int] = 0):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    user_data = {
        "logged_in_user":logged_in_user,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }

    sql = card_post_private(**user_data)

    if type_name == 'my-post':
        where = " and p.user_id={logged_in_user}".format(logged_in_user=logged_in_user)
        orderby = " created_at desc"

    if type_name == 'my-bookmark':
        where = " and ab.id notnull"
        orderby = " created_at_bookmark desc"
    
    if type_name == 'my-like':
        where = " and al.id notnull"
        orderby = " created_at_like desc"
    
    if type_name == 'my-comment-post':
        where = " and ac.id notnull"
        orderby = " created_at_comment desc"

    orderby = " order by {orderby} nulls last limit {limit} offset {offset}".format(orderby=orderby,limit=limit,offset=offset)

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(card_post_private_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")


# get card-post single
@router.get("/post/{post_id}", status_code=status.HTTP_200_OK)
async def card_post_single(request:Request,post_id:str):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    user_data = {
        "logged_in_user":logged_in_user,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }
    sql = card_post_private(**user_data)
    where = " and p.id={post_id}".format(post_id=post_id)
    sql = sql + where 
    print(sql)
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(card_post_private_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")

