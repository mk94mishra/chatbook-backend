from copy import deepcopy
from typing import Optional
import json
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
from common.response import error_response, success_response

router = APIRouter(prefix='/v1/public', tags=["public-card-post"])


# get card all post
@router.get("/card-post", status_code=status.HTTP_200_OK)
async def card_post_all(community_id: Optional[int] = 0,category_id: Optional[int] = 0, user_type_id: Optional[int] = 0, description: Optional[str] = None, limit: Optional[int] = 10, offset: Optional[int] = 0, order_by: Optional[str] = 'p.created_at desc'):
    try:
        async with in_transaction() as connection:
            sql = """select p.* from tbl_card_post as p"""
            where = " where p.is_active='true' "

            if user_type_id:
                where = where + " and p.user_type_id={user_type_id}".format(user_type_id=user_type_id)
            if community_id:
                where = where + " and p.community_id={community_id}".format(community_id=community_id)
            if category_id:
                where = where + " and p.category_id={category_id}".format(category_id=category_id)
            if description:
                where = " where p.is_active='true' and lower(p.description) LIKE '%{description}%'".format(description=description.lower())
            
            orderby = " order by {order_by} nulls last limit {limit} offset {offset}".format(order_by=order_by, limit=limit,offset=offset)

            sql = sql + where + orderby
            print(sql)
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
                    "user_type_id": card_single['user_type_id'],
                    "count_like": card_single['count_like'],
                    "count_comment": card_single['count_comment'],
                    "community_id": card_single['community_id'],
                    "category_id": card_single['category_id'],
                    "category_name": card_single['category_name'],
                }
                card_post_list.append(post)
            return success_response(card_post_list)
    except OperationalError:
        return error_response(code=400, message="something error!")
    

# get card single post
@router.get("/card-post/post/{post_id}", status_code=status.HTTP_200_OK)
async def card_post_single(post_id: int):
    try:
        async with in_transaction() as connection:
            sql = "select p.* from tbl_card_post as p"
            where = " where p.id = {post_id} and p.is_active='true'".format(post_id=post_id)
            
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
                    "user_type_id": card_single['user_type_id'],
                    "count_like": card_single['count_like'],
                    "count_comment": card_single['count_comment'],
                    "community_id": card_single['community_id'],
                    "category_id": card_single['category_id'],
                    "category_name": card_single['category_name'],
                }
                card_post_list.append(post)
            return success_response(card_post_list)
    except OperationalError:
        return error_response(code=400, message="something error!")

    
# get card user post
@router.get("/card-post/user/{user_id}", status_code=status.HTTP_200_OK)
async def card_post_user(user_id: int,category_id: Optional[int] = 0, limit: Optional[int] = 10, offset: Optional[int] = 0, order_by: Optional[str] = 'p.created_at desc'):
    try:
        async with in_transaction() as connection:
            sql = "select p.* from tbl_card_post as p"
            where = " where p.user_id = {user_id} and p.is_active='true'".format(user_id=user_id)
  
            if category_id:
                where = where + " and p.category_id={category_id}".format(category_id=category_id)
            
            orderby = " order by {order_by} nulls last limit {limit} offset {offset}".format(order_by=order_by, limit=limit,offset=offset)

            sql = sql + where + orderby
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
                    "user_type_id": card_single['user_type_id'],
                    "count_like": card_single['count_like'],
                    "count_comment": card_single['count_comment'],
                    "community_id": card_single['community_id'],
                    "category_id": card_single['category_id'],
                    "category_name": card_single['category_name'],
                }
                card_post_list.append(post)
            return success_response(card_post_list)
    except OperationalError:
        return error_response(code=400, message="something error!")

