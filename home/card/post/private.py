from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, OperationalError
import json
from common.response import error_response, success_response

from user.models import User

router = APIRouter(prefix='/v1/private', tags=["private-card-post"])


# get card-post all
@router.get("/card-post", status_code=status.HTTP_200_OK)
async def card_post_all(request:Request, community_id: Optional[int] = 0,category_id: Optional[int] = 0, designation_id: Optional[int] = 0, description: Optional[str] = None, limit: Optional[int] = 10, offset: Optional[int] = 0, order_by: Optional[str] = 'p.created_at desc'):
    logged_in_user = request.state.user_id
    user = await User.get(id=logged_in_user)
    self_user_lat = user.lat
    self_user_long = user.long
    try:
        async with in_transaction() as connection:
            sql = """
            with
            lpu as (select lpu.post_id, lpu.created_at, true as is_like from tbl_like_post as lpu where lpu.user_id={logged_in_user}),
            bpu as (select bu.post_id, bu.created_at, true as is_bookmark from tbl_bookmark as bu where bu.user_id={logged_in_user}),
            cpu as (select c.post_id, max(c.created_at) as created_at, true as is_comment from tbl_comment as c where c.user_id={logged_in_user} and c.is_active=true group by c.post_id),
            ub as (select ub1.user_id_blocked  as user_id, true as is_block from tbl_user_block as ub1  where ub1.user_id={logged_in_user} union select ub2.user_id  as user_id, true as is_block from tbl_user_block as ub2 where ub2.user_id_blocked={logged_in_user})
            select 
            p.*,
            lpu.is_like,
            bpu.is_bookmark,
            cpu.is_comment,
            ub.is_block,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join lpu on p.id=lpu.post_id
            left join bpu on p.id=bpu.post_id
            left join cpu on p.id=cpu.post_id
            left join ub on p.user_id=ub.user_id
            """.format(logged_in_user=logged_in_user, self_user_lat=self_user_lat, self_user_long=self_user_long)

            where = "where ub.is_block isnull"
            if user_type_id:
                where = where + " and p.designation_id={user_type_id}".format(user_type_id=user_type_id)
            if community_id:
                where = where + " and p.community_id={community_id}".format(community_id=community_id)
            if category_id:
                where = where + " and p.category_id={category_id}".format(category_id=category_id)
            if description:
                where = " where ub.is_block isnull and lower(p.description) LIKE '%{description}%'".format(description=description.lower())
            
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
                    "is_like":card_single['is_like'],
                    "is_bookmark":card_single['is_bookmark']
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
            lpu as (select lpu.post_id, lpu.created_at, true as is_like from tbl_like_post as lpu where lpu.user_id={logged_in_user}),
            bpu as (select bu.post_id, bu.created_at, true as is_bookmark from tbl_bookmark as bu where bu.user_id={logged_in_user}),
            cpu as (select c.post_id, max(c.created_at) as created_at, true as is_comment from tbl_comment as c where c.user_id={logged_in_user} and c.is_active=true group by c.post_id),
            ub as (select ub1.user_id_blocked  as user_id, true as is_block from tbl_user_block as ub1  where ub1.user_id={logged_in_user} union select ub2.user_id  as user_id, true as is_block from tbl_user_block as ub2 where ub2.user_id_blocked={logged_in_user})
            select 
            p.*,
            lpu.is_like,
            bpu.is_bookmark,
            cpu.is_comment,
            ub.is_block,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join lpu on p.id=lpu.post_id
            left join bpu on p.id=bpu.post_id
            left join cpu on p.id=cpu.post_id
            left join ub on p.user_id=ub.user_id
            """.format(logged_in_user=logged_in_user, self_user_lat=self_user_lat, self_user_long=self_user_long)

            where = "where ub.is_block isnull and p.id={post_id}".format(post_id=post_id)

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
                    "is_like":card_single['is_like'],
                    "is_bookmark":card_single['is_bookmark']
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
            lpu as (select lpu.post_id, lpu.created_at, true as is_like from tbl_like_post as lpu where lpu.user_id={logged_in_user}),
            bpu as (select bu.post_id, bu.created_at, true as is_bookmark from tbl_bookmark as bu where bu.user_id={logged_in_user}),
            cpu as (select c.post_id, max(c.created_at) as created_at, true as is_comment from tbl_comment as c where c.user_id={logged_in_user} and c.is_active=true group by c.post_id),
            ub as (select ub1.user_id_blocked  as user_id, true as is_block from tbl_user_block as ub1  where ub1.user_id={logged_in_user} union select ub2.user_id  as user_id, true as is_block from tbl_user_block as ub2 where ub2.user_id_blocked={logged_in_user})
            select 
            p.*,
            lpu.is_like,
            bpu.is_bookmark,
            cpu.is_comment,
            ub.is_block,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join lpu on p.id=lpu.post_id
            left join bpu on p.id=bpu.post_id
            left join cpu on p.id=cpu.post_id
            left join ub on p.user_id=ub.user_id
            """.format(logged_in_user=logged_in_user, self_user_lat=self_user_lat, self_user_long=self_user_long)

            where = " where p.user_id = {user_id} and ub.is_block isnull".format(user_id=user_id)

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
                    "is_like":card_single['is_like'],
                    "is_bookmark":card_single['is_bookmark']
                }
                card_post_list.append(post)
            return success_response(card_post_list)
    except OperationalError:
        return error_response(code=400, message="something error!")



# get card-post all community
@router.get("/card-post/community/{community_id}", status_code=status.HTTP_200_OK)
async def card_post_community(request:Request, community_id:int,category_id: Optional[int] = 0, designation_id: Optional[int] = 0,description: Optional[str] =None, limit: Optional[int] = 10, offset: Optional[int] = 0, order_by: Optional[str] = 'p.created_at desc'):
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
            lpu as (select lpu.post_id, lpu.created_at, true as is_like from tbl_like_post as lpu where lpu.user_id={logged_in_user}),
            bpu as (select bu.post_id, bu.created_at, true as is_bookmark from tbl_bookmark as bu where bu.user_id={logged_in_user}),
            cpu as (select c.post_id, max(c.created_at) as created_at, true as is_comment from tbl_comment as c where c.user_id={logged_in_user} and c.is_active=true group by c.post_id),
            ub as (select ub1.user_id_blocked  as user_id, true as is_block from tbl_user_block as ub1  where ub1.user_id={logged_in_user} union select ub2.user_id  as user_id, true as is_block from tbl_user_block as ub2 where ub2.user_id_blocked={logged_in_user})
            select 
            p.*,
            lpu.is_like,
            bpu.is_bookmark,
            cpu.is_comment,
            ub.is_block,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join lpu on p.id=lpu.post_id
            left join bpu on p.id=bpu.post_id
            left join cpu on p.id=cpu.post_id
            left join ub on p.user_id=ub.user_id
            """.format(logged_in_user=logged_in_user,self_user_lat=self_user_lat,self_user_long=self_user_long)

            where = " where ub.is_block isnull"

            if user_type_id:
                where = where + " and p.designation_id={user_type_id}".format(user_type_id=user_type_id)
            if community_id:
                where = where + " and p.community_id={community_id}".format(community_id=community_id)
            if category_id:
                where = where + " and p.category_id={category_id}".format(category_id=category_id)
            if description:
                where = " where ub.is_block isnull and p.community_id={community_id} and lower(p.description) LIKE '%{description}%'".format( community_id=community_id,description=description.lower())
            
            
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
                    "is_like":card_single['is_like'],
                    "is_bookmark":card_single['is_bookmark']
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
            lpu as (select lpu.post_id, lpu.created_at, true as is_like from tbl_like_post as lpu where lpu.user_id={logged_in_user}),
            bpu as (select bu.post_id, bu.created_at, true as is_bookmark from tbl_bookmark as bu where bu.user_id={logged_in_user}),
            cpu as (select c.post_id, max(c.created_at) as created_at, true as is_comment from tbl_comment as c where c.user_id={logged_in_user} and c.is_active=true group by c.post_id),
            ub as (select ub1.user_id_blocked  as user_id, true as is_block from tbl_user_block as ub1  where ub1.user_id={logged_in_user} union select ub2.user_id  as user_id, true as is_block from tbl_user_block as ub2 where ub2.user_id_blocked={logged_in_user})
            select 
            p.*,
            lpu.is_like,
            bpu.is_bookmark,
            cpu.is_comment,
            ub.is_block,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join lpu on p.id=lpu.post_id
            left join bpu on p.id=bpu.post_id
            left join cpu on p.id=cpu.post_id
            left join ub on p.user_id=ub.user_id
            """.format(logged_in_user=logged_in_user,self_user_lat=self_user_lat, self_user_long=self_user_long)

            where = " where ub.is_block isnull and cpu.is_comment=true"
            
            orderby = " order by cpu.created_at desc limit {limit} offset {offset}".format(limit=limit,offset=offset)

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
                    "is_comment":card_single['is_comment'],
                    "is_like":card_single['is_like'],
                    "is_bookmark":card_single['is_bookmark']
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
            lpu as (select lpu.post_id, lpu.created_at, true as is_like from tbl_like_post as lpu where lpu.user_id={logged_in_user}),
            bpu as (select bu.post_id, bu.created_at, true as is_bookmark from tbl_bookmark as bu where bu.user_id={logged_in_user}),
            cpu as (select c.post_id, max(c.created_at) as created_at, true as is_comment from tbl_comment as c where c.user_id={logged_in_user} and c.is_active=true group by c.post_id),
            ub as (select ub1.user_id_blocked  as user_id, true as is_block from tbl_user_block as ub1  where ub1.user_id={logged_in_user} union select ub2.user_id  as user_id, true as is_block from tbl_user_block as ub2 where ub2.user_id_blocked={logged_in_user})
            select 
            p.*,
            lpu.is_like,
            bpu.is_bookmark,
            cpu.is_comment,
            ub.is_block,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join lpu on p.id=lpu.post_id
            left join bpu on p.id=bpu.post_id
            left join cpu on p.id=cpu.post_id
            left join ub on p.user_id=ub.user_id
            """.format(logged_in_user=logged_in_user, self_user_lat=self_user_lat,self_user_long=self_user_long)

            where = " where ub.is_block isnull and lpu.is_like=true" 
            
            orderby = " order by lpu.created_at desc limit {limit} offset {offset}".format(limit=limit,offset=offset)

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
                    "is_like":card_single['is_like'],
                    "is_bookmark":card_single['is_bookmark']
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
            lpu as (select lpu.post_id, lpu.created_at, true as is_like from tbl_like_post as lpu where lpu.user_id={logged_in_user}),
            bpu as (select bu.post_id, bu.created_at, true as is_bookmark from tbl_bookmark as bu where bu.user_id={logged_in_user}),
            cpu as (select c.post_id, max(c.created_at) as created_at, true as is_comment from tbl_comment as c where c.user_id={logged_in_user} and c.is_active=true group by c.post_id),
            ub as (select ub1.user_id_blocked  as user_id, true as is_block from tbl_user_block as ub1  where ub1.user_id={logged_in_user} union select ub2.user_id  as user_id, true as is_block from tbl_user_block as ub2 where ub2.user_id_blocked={logged_in_user})
            select 
            p.*,
            lpu.is_like,
            bpu.is_bookmark,
            cpu.is_comment,
            ub.is_block,
            st_distance(st_makepoint(p.lat,p.long), st_makepoint({self_user_lat},{self_user_long})) as distance
            from tbl_card_post as p
            left join lpu on p.id=lpu.post_id
            left join bpu on p.id=bpu.post_id
            left join cpu on p.id=cpu.post_id
            left join ub on p.user_id=ub.user_id
            """.format(logged_in_user=logged_in_user,self_user_lat=self_user_lat,self_user_long=self_user_long)

            where = " where ub.is_block isnull and bpu.is_bookmark=true"

            orderby = " order by bpu.created_at desc limit {limit} offset {offset}".format(limit=limit,offset=offset)

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
                    "is_like":card_single['is_like'],
                    "is_bookmark":card_single['is_bookmark']
                }
                card_post_list.append(post)
            return success_response(card_post_list)
    except OperationalError:
        return error_response(code=400, message="something error!")
