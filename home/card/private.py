from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from user.models import User

from home.card.query_function import card_post_private

router = APIRouter(prefix='/v1/private', tags=["private-card-post"])


# get card-post all
@router.get("/card-post", status_code=status.HTTP_200_OK)
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




# get card-post single post
@router.get("/card-post/post/{post_id}", status_code=status.HTTP_200_OK)
async def card_post_single(request:Request, post_id:int):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    self_user_lat = user.lat
    self_user_long = user.long
    try:
        async with in_transaction() as connection:
            sql = """
            with
            al as (select id,post_id,created_at from tbl_action where type='like' and user_id={logged_in_user}),
            ac as (select array_agg(id) as id, post_id, max(created_at) as created_at from tbl_action where type='comment' and user_id={logged_in_user} group by post_id),
            abo as (select id,post_id ,created_at from tbl_action where type='bookmark' and user_id={logged_in_user}),
            asp as (select id,post_id ,created_at from tbl_action where type='spam' and user_id={logged_in_user}),
            ab1 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id={logged_in_user}),
            ab2 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id_blocked_id ={logged_in_user})

            select 
            p.*,
            al.id as action_id_like,al.created_at as created_at_like,
            ac.id as action_id_comment,ac.created_at as created_at_comment,
            abo.id as action_id_bookmark,abo.created_at as created_at_bookmark,
            asp.id as action_id_spam, asp.created_at as created_at_spam,
            ab1.id as action_id_block,
            ab2.id as action_id_block_me,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join al on p.id=al.post_id
            left join ac on p.id=ac.post_id
            left join abo on p.id=abo.post_id
            left join asp on p.id=asp.post_id
            left join ab1 on p.user_id=ab1.user_id_blocked_id
            left join ab2 on p.user_id=ab2.user_id
            """.format(logged_in_user=logged_in_user, self_user_lat=self_user_lat, self_user_long=self_user_long)

            where = "where action_id_block isnull and action_id_block_me isnull and p.id={post_id}".format(post_id=post_id)

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



# get card user post
@router.get("/card-post/user/{user_id}", status_code=status.HTTP_200_OK)
async def card_post_user(request:Request, user_id: int,category_id: Optional[int] = 0, limit: Optional[int] = 10, offset: Optional[int] = 0, order_by: Optional[str] = 'p.created_at desc'):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    self_user_lat = user.lat
    self_user_long = user.long
    try:
        async with in_transaction() as connection:
            sql = """
            with
            al as (select id,post_id,created_at from tbl_action where type='like' and user_id={logged_in_user}),
            ac as (select array_agg(id) as id, post_id, max(created_at) as created_at from tbl_action where type='comment' and user_id={logged_in_user} group by post_id),
            abo as (select id,post_id ,created_at from tbl_action where type='bookmark' and user_id={logged_in_user}),
            asp as (select id,post_id ,created_at from tbl_action where type='spam' and user_id={logged_in_user}),
            ab1 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id={logged_in_user}),
            ab2 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id_blocked_id ={logged_in_user})

            select 
            p.*,
            al.id as action_id_like,al.created_at as created_at_like,
            ac.id as action_id_comment,ac.created_at as created_at_comment,
            abo.id as action_id_bookmark,abo.created_at as created_at_bookmark,
            asp.id as action_id_spam, asp.created_at as created_at_spam,
            ab1.id as action_id_block,
            ab2.id as action_id_block_me,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join al on p.id=al.post_id
            left join ac on p.id=ac.post_id
            left join abo on p.id=abo.post_id
            left join asp on p.id=asp.post_id
            left join ab1 on p.user_id=ab1.user_id_blocked_id
            left join ab2 on p.user_id=ab2.user_id
            """.format(logged_in_user=logged_in_user, self_user_lat=self_user_lat, self_user_long=self_user_long)

            where = " where p.user_id = {user_id} and action_id_block isnull and action_id_block_me isnull".format(user_id=user_id)

            if category_id:
                where = " and p.category_id={category_id}".format(category_id=category_id)
            
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



# get card-post all community
@router.get("/card-post/community/{community_id}", status_code=status.HTTP_200_OK)
async def card_post_community(request:Request, community_id:int,category_id: Optional[int] = 0, designation_id: Optional[int] = 0,description: Optional[str] =None,trending: Optional[int] =None, limit: Optional[int] = 10, offset: Optional[int] = 0, order_by: Optional[str] = 'p.created_at desc'):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    self_user_lat = user.lat
    self_user_long = user.long
    # self user community check
    if community_id != user.community_id:
        return error_response(code=401, message="you don't have permission!")

    try:
        async with in_transaction() as connection:
            sql = """
            with
            al as (select id,post_id,created_at from tbl_action where type='like' and user_id={logged_in_user}),
            ac as (select array_agg(id) as id, post_id, max(created_at) as created_at from tbl_action where type='comment' and user_id={logged_in_user} group by post_id),
            abo as (select id,post_id ,created_at from tbl_action where type='bookmark' and user_id={logged_in_user}),
            asp as (select id,post_id ,created_at from tbl_action where type='spam' and user_id={logged_in_user}),
            ab1 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id={logged_in_user}),
            ab2 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id_blocked_id ={logged_in_user})

            select 
            p.*,
            al.id as action_id_like,al.created_at as created_at_like,
            ac.id as action_id_comment,ac.created_at as created_at_comment,
            abo.id as action_id_bookmark,abo.created_at as created_at_bookmark,
            asp.id as action_id_spam, asp.created_at as created_at_spam,
            ab1.id as action_id_block,
            ab2.id as action_id_block_me,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join al on p.id=al.post_id
            left join ac on p.id=ac.post_id
            left join abo on p.id=abo.post_id
            left join asp on p.id=asp.post_id
            left join ab1 on p.user_id=ab1.user_id_blocked_id
            left join ab2 on p.user_id=ab2.user_id
            """.format(logged_in_user=logged_in_user,self_user_lat=self_user_lat,self_user_long=self_user_long)

            where = " where action_id_block isnull and action_id_block_me isnull"

            if designation_id:
                where = where + " and p.designation_id={user_type_id}".format(designation_id=designation_id)
            if community_id:
                where = where + " and p.community_id={community_id}".format(community_id=community_id)
            if category_id:
                where = where + " and p.category_id={category_id}".format(category_id=category_id)
            if description:
                where = " where action_id_block isnull and action_id_block_me isnull and p.community_id={community_id} and lower(p.description) LIKE '%{description}%'".format( community_id=community_id,description=description.lower())
            
            if trending:
                where = " where p.community_id={community_id} and action_id_block isnull and action_id_block_me isnull and ageing <=1".format(community_id=community_id)
                order_by = 'ageing desc'
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



# get card-post commented
@router.get("/card-post/commented", status_code=status.HTTP_200_OK)
async def card_post_commented(request:Request, limit: Optional[int] = 10, offset: Optional[int] = 0):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    self_user_lat = user.lat
    self_user_long = user.long
    try:
        async with in_transaction() as connection:
            sql = """
            with
            al as (select id,post_id,created_at from tbl_action where type='like' and user_id={logged_in_user}),
            ac as (select array_agg(id) as id, post_id, max(created_at) as created_at from tbl_action where type='comment' and user_id={logged_in_user} group by post_id),
            abo as (select id,post_id ,created_at from tbl_action where type='bookmark' and user_id={logged_in_user}),
            asp as (select id,post_id ,created_at from tbl_action where type='spam' and user_id={logged_in_user}),
            ab1 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id={logged_in_user}),
            ab2 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id_blocked_id ={logged_in_user})

            select 
            p.*,
            al.id as action_id_like,al.created_at as created_at_like,
            ac.id as action_id_comment,ac.created_at as created_at_comment,
            abo.id as action_id_bookmark,abo.created_at as created_at_bookmark,
            asp.id as action_id_spam, asp.created_at as created_at_spam,
            ab1.id as action_id_block,
            ab2.id as action_id_block_me,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join al on p.id=al.post_id
            left join ac on p.id=ac.post_id
            left join abo on p.id=abo.post_id
            left join asp on p.id=asp.post_id
            left join ab1 on p.user_id=ab1.user_id_blocked_id
            left join ab2 on p.user_id=ab2.user_id
            """.format(logged_in_user=logged_in_user,self_user_lat=self_user_lat, self_user_long=self_user_long)

            where = " where action_id_block isnull and action_id_block_me isnull and action_id_comment notnull"
            
            orderby = " order by ac.created_at desc limit {limit} offset {offset}".format(limit=limit,offset=offset)

            sql = sql +  where + orderby
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


# get card-post liked
@router.get("/card-post/liked", status_code=status.HTTP_200_OK)
async def card_post_liked(request:Request, limit: Optional[int] = 10, offset: Optional[int] = 0):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    self_user_lat = user.lat
    self_user_long = user.long
    try:
        async with in_transaction() as connection:
            sql = """
            with
            al as (select id,post_id,created_at from tbl_action where type='like' and user_id={logged_in_user}),
            ac as (select array_agg(id) as id, post_id, max(created_at) as created_at from tbl_action where type='comment' and user_id={logged_in_user} group by post_id),
            abo as (select id,post_id ,created_at from tbl_action where type='bookmark' and user_id={logged_in_user}),
            asp as (select id,post_id ,created_at from tbl_action where type='spam' and user_id={logged_in_user}),
            ab1 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id={logged_in_user}),
            ab2 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id_blocked_id ={logged_in_user})

            select 
            p.*,
            al.id as action_id_like,al.created_at as created_at_like,
            ac.id as action_id_comment,ac.created_at as created_at_comment,
            abo.id as action_id_bookmark,abo.created_at as created_at_bookmark,
            asp.id as action_id_spam, asp.created_at as created_at_spam,
            ab1.id as action_id_block,
            ab2.id as action_id_block_me,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join al on p.id=al.post_id
            left join ac on p.id=ac.post_id
            left join abo on p.id=abo.post_id
            left join asp on p.id=asp.post_id
            left join ab1 on p.user_id=ab1.user_id_blocked_id
            left join ab2 on p.user_id=ab2.user_id
            """.format(logged_in_user=logged_in_user, self_user_lat=self_user_lat,self_user_long=self_user_long)

            where = " where action_id_block isnull and action_id_block_me isnull and action_id_like notnull" 
            
            orderby = " order by created_at_like desc limit {limit} offset {offset}".format(limit=limit,offset=offset)

            sql = sql +  where + orderby
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


# get card-post bookmarked
@router.get("/card-post/bookmarked", status_code=status.HTTP_200_OK)
async def card_post_bookmarked(request:Request, limit: Optional[int] = 10, offset: Optional[int] = 0):

    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    self_user_lat = user.lat
    self_user_long = user.long
    try:
        async with in_transaction() as connection:
            sql = """
            with
            al as (select id,post_id,created_at from tbl_action where type='like' and user_id={logged_in_user}),
            ac as (select array_agg(id) as id, post_id, max(created_at) as created_at from tbl_action where type='comment' and user_id={logged_in_user} group by post_id),
            abo as (select id,post_id ,created_at from tbl_action where type='bookmark' and user_id={logged_in_user}),
            asp as (select id,post_id ,created_at from tbl_action where type='spam' and user_id={logged_in_user}),
            ab1 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id={logged_in_user}),
            ab2 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id_blocked_id ={logged_in_user})

            select 
            p.*,
            al.id as action_id_like,al.created_at as created_at_like,
            ac.id as action_id_comment,ac.created_at as created_at_comment,
            abo.id as action_id_bookmark,abo.created_at as created_at_bookmark,
            asp.id as action_id_spam, asp.created_at as created_at_spam,
            ab1.id as action_id_block,
            ab2.id as action_id_block_me,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join al on p.id=al.post_id
            left join ac on p.id=ac.post_id
            left join abo on p.id=abo.post_id
            left join asp on p.id=asp.post_id
            left join ab1 on p.user_id=ab1.user_id_blocked_id
            left join ab2 on p.user_id=ab2.user_id
            """.format(logged_in_user=logged_in_user,self_user_lat=self_user_lat,self_user_long=self_user_long)

            where = " where action_id_block isnull and action_id_block_me isnull "

            orderby = " order by created_at_bookmark desc limit {limit} offset {offset}".format(limit=limit,offset=offset)

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
