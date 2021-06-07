from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from atom.user.models import User

from atom.feed.post.schemas import Feed
from atom.helper.helper import post_master_token, post_master_token_response

router = APIRouter(prefix='/v1/token/feed-post', tags=["token-feed-post"])


# get feed-post fresh
@router.post("/fresh", status_code=status.HTTP_200_OK)
async def post_master_fresh(request:Request,payload: Feed):
    data = deepcopy(payload.dict())
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    logged_in_lat = user.lat
    logged_in_long = user.long
    user_data = {
        "logged_in_user_id": logged_in_user_id,
        "logged_in_lat":logged_in_lat,
        "logged_in_long":logged_in_long
    }
    sql = post_master_token(**user_data)

    where = ""

    if data['distance']:
        where = where + " and st_distance(st_makepoint(p.lat,p.long), st_makepoint({logged_in_lat},{logged_in_long})) <= {distance}".format(logged_in_lat=logged_in_lat,logged_in_long=logged_in_long,distance=data['distance'])
    if data['gender']:
        where = where + " and gender = '{gender}'".format(gender=data['gender'])
    
    if data['description']:
        where = where + " and description like '%{description}%'".format(description=data['description'])

    if data['category_id']:
        where = where + " and category_id = {category_id}".format(category_id=data['category_id'])

    if data['designation_id']:
        where = where + " and designation_id = {designation_id}".format(designation_id=data['designation_id'])

    orderby = " order by created_at desc nulls last limit {limit} offset {offset}".format(limit=data['limit'],offset=data['offset'])

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            post_master = await connection.execute_query(sql)
            return success_response(post_master_token_response(post_master[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")



# get feed-post most liked
@router.post("/most-liked", status_code=status.HTTP_200_OK)
async def post_master_most_liked(request:Request,payload: Feed):
    data = deepcopy(payload.dict())
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    logged_in_lat = user.lat
    logged_in_long = user.long
    user_data = {
        "logged_in_user_id": logged_in_user_id,
        "logged_in_lat":logged_in_lat,
        "logged_in_long":logged_in_long
    }
    sql = post_master_token(**user_data)

    where = ""

    if data['distance']:
        where = where + " and st_distance(st_makepoint(p.lat,p.long), st_makepoint({logged_in_lat},{logged_in_long})) <= {distance}".format(logged_in_lat=logged_in_lat,logged_in_long=logged_in_long,distance=data['distance'])
    if data['gender']:
        where = where + " and gender = '{gender}'".format(gender=data['gender'])
    
    if data['description']:
        where = where + " and description like '%{description}%'".format(description=data['description'])

    if data['category_id']:
        where = where + " and category_id = {category_id}".format(category_id=data['category_id'])

    if data['designation_id']:
        where = where + " and designation_id = {designation_id}".format(designation_id=data['designation_id'])

    orderby = " order by count_like desc nulls last limit {limit} offset {offset}".format(limit=data['limit'],offset=data['offset'])

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            post_master = await connection.execute_query(sql)
            return success_response(post_master_token_response(post_master[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")



# get feed-post trending
@router.post("/trending", status_code=status.HTTP_200_OK)
async def post_master_trending(request:Request,payload: Feed):
    data = deepcopy(payload.dict())
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    logged_in_lat = user.lat
    logged_in_long = user.long
    user_data = {
        "logged_in_user_id": logged_in_user_id,
        "logged_in_lat":logged_in_lat,
        "logged_in_long":logged_in_long
    }
    sql = post_master_token(**user_data)

    where = " and p.ageing <= 1"

    if data['distance']:
        where = where + " and st_distance(st_makepoint(p.lat,p.long), st_makepoint({logged_in_lat},{logged_in_long})) <= {distance}".format(logged_in_lat=logged_in_lat,logged_in_long=logged_in_long,distance=data['distance'])
    if data['gender']:
        where = where + " and gender = '{gender}'".format(gender=data['gender'])
    
    if data['description']:
        where = where + " and description like '%{description}%'".format(description=data['description'])

    if data['category_id']:
        where = where + " and category_id = {category_id}".format(category_id=data['category_id'])

    if data['designation_id']:
        where = where + " and designation_id = {designation_id}".format(designation_id=data['designation_id'])

    orderby = " order by count_like desc nulls last limit {limit} offset {offset}".format(limit=data['limit'],offset=data['offset'])

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            post_master = await connection.execute_query(sql)
            return success_response(post_master_token_response(post_master[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")



# get feed-post my-post
@router.get("/my-post", status_code=status.HTTP_200_OK)
async def post_master_my_post(request:Request,limit:Optional[int] = 10, offset:Optional[int] = 0):
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    user_data = {
        "logged_in_user_id":logged_in_user_id,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }

    sql = post_master_token(**user_data)
    where = " and p.user_id={logged_in_user_id}".format(logged_in_user_id=logged_in_user_id)
    orderby = " p.created_at desc"
    
    orderby = " order by {orderby} nulls last limit {limit} offset {offset}".format(orderby=orderby,limit=limit,offset=offset)

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(post_master_token_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")



# get feed-post my bookmark
@router.get("/my-bookmarked-post", status_code=status.HTTP_200_OK)
async def post_master_my_bookmark(request:Request,limit:Optional[int] = 10, offset:Optional[int] = 0):
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    user_data = {
        "logged_in_user_id":logged_in_user_id,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }

    sql = post_master_token(**user_data)
    where = " and abo.id notnull"
    orderby = " abo.created_at desc"
    
    orderby = " order by {orderby} nulls last limit {limit} offset {offset}".format(orderby=orderby,limit=limit,offset=offset)

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(post_master_token_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")


# get feed-post my like
@router.get("/my-liked-post", status_code=status.HTTP_200_OK)
async def post_master_my_like(request:Request,limit:Optional[int] = 10, offset:Optional[int] = 0):
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    user_data = {
        "logged_in_user_id":logged_in_user_id,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }

    sql = post_master_token(**user_data)
    where = " and al.id notnull"
    orderby = " al.created_at desc"
    
    orderby = " order by {orderby} nulls last limit {limit} offset {offset}".format(orderby=orderby,limit=limit,offset=offset)

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(post_master_token_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")


# get feed-post my-commented-post
@router.get("/my-commented-post", status_code=status.HTTP_200_OK)
async def post_master_my_comment_post(request:Request,limit:Optional[int] = 10, offset:Optional[int] = 0):
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    user_data = {
        "logged_in_user_id":logged_in_user_id,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }

    sql = post_master_token(**user_data)
    where = " and ac.id notnull"
    orderby = " ac.created_at desc"

    orderby = " order by {orderby} nulls last limit {limit} offset {offset}".format(orderby=orderby,limit=limit,offset=offset)

    sql = sql + where + orderby
    print(sql)
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(post_master_token_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")



# get feed-post single
@router.get("/post/{post_id}", status_code=status.HTTP_200_OK)
async def post_master_single(request:Request,post_id:int):
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    user_data = {
        "logged_in_user_id":logged_in_user_id,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }
    sql = post_master_token(**user_data)
    where = " and p.id={post_id}".format(post_id=post_id)
    sql = sql + where 
    print(sql)
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(post_master_token_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")



# get feed-post single user
@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def post_master_user(request:Request,user_id:int):
    logged_in_user_id = request.state.user_id
    user = await User.get(id=logged_in_user_id)
    user_data = {
        "logged_in_user_id":logged_in_user_id,
        "logged_in_lat" :user.lat,
        "logged_in_long" :user.long
    }
    sql = post_master_token(**user_data)
    where = " and p.user_id={user_id}".format(user_id=user_id)
    sql = sql + where 
    print(sql)
    try:
        async with in_transaction() as connection:
            card_post = await connection.execute_query(sql)
            return success_response(post_master_token_response(card_post[1]))
    except OperationalError:
        return error_response(code=400, message="something error!")

