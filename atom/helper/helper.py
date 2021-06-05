import json
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction

from common.response import error_response, success_response

def post_master_token(**data):
    sql = """
        with
        l as (select id,post_id,created_at from tbl_like_post where user_id={logged_in_user_id}),
        c as (select array_agg(id) as id, post_id, max(created_at) as created_at from tbl_comment where user_id={logged_in_user_id} group by post_id),
        bo as (select id,post_id ,created_at from tbl_bookmark where user_id={logged_in_user_id}),
        sp as (select id,post_id ,created_at from tbl_spam where user_id={logged_in_user_id}),
        r as (select id,user_rated_id, rating,created_at from tbl_rating where user_id={logged_in_user_id}),
        b1 as (select id, user_id, user_blocked_id from tbl_block  where user_id={logged_in_user_id}),
        b2 as (select id, user_id, user_blocked_id from tbl_block where user_blocked_id ={logged_in_user_id}),
        cr as (select receiver_id, count(id) as count_pending_request from tbl_chat_request where sender_id={logged_in_user_id} and is_activated isnull group by receiver_id)

        select 
        p.*,
        l.id as like_id,l.created_at as like_created_at,
        c.id as comment_id,c.created_at as comment_created_at,
        bo.id as bookmark_id,bo.created_at as bookmark_created_at,
        sp.id as spam_id, sp.created_at as spam_created_at,
        r.id as rating_id, r.rating as rated, r.created_at as rating_created_at,
        b1.id as id_block,
        b2.id as id_block_me,
        st_distance(st_makepoint(p.lat,p.long), st_makepoint({logged_in_lat},{logged_in_long})) as distance,
        cr.count_pending_request
        from tbl_post_master as p
        left join l on p.id=l.post_id
        left join c on p.id=c.post_id
        left join bo on p.id=bo.post_id
        left join sp on p.id=sp.post_id
        left join r on p.user_id=r.user_rated_id
        left join b1 on p.user_id=b1.user_blocked_id
        left join b2 on p.user_id=b2.user_id
        left join cr on p.user_id=cr.receiver_id
        where is_active=true 
        and b1.id isnull
        and b2.id isnull
        """.format(logged_in_user_id=data['logged_in_user_id'],logged_in_lat=data['logged_in_lat'],logged_in_long=data['logged_in_long'])
    
    return sql


def post_master_token_response(data):
    card_post_list = list()
    for card_single in data:
        media_data = None
        if card_single['media'] != None:
            media_data = json.loads(card_single['media'])

        post = {
            "post_id":card_single['id'],
            "created_at":str(card_single['created_at']),
            "description":card_single['description'],
            "media":media_data,
            "community_id":card_single['community_id'],
            "community_name":card_single['community_name'],
            "category_id":card_single['category_id'],
            "category_name":card_single['category_name'],
            "user_id":card_single['user_id'],
            "username":card_single['username'],
            "profile_pic_url":card_single['profile_pic_url'],
            "gender":card_single['gender'],
            "designation_id":card_single['designation_id'],
            "rating":card_single['rating'],
            "ageing":card_single['ageing'],
            "lat":card_single['lat'],
            "long":card_single['long'],
            "count_like":card_single['count_like'],
            "count_comment":card_single['count_comment'],

            "like_id":card_single['like_id'],
            "like_created_at":card_single['like_created_at'],
            "comment_id":card_single['comment_id'],
            "comment_created_at":card_single['comment_created_at'],
            "bookmark_id":card_single['bookmark_id'],
            "bookmark_created_at":card_single['bookmark_created_at'],
            "spam_id":card_single['spam_id'],
            "spam_created_at":card_single['spam_created_at'],
            "rating_id":card_single['rating_id'],
            "rating_created_at":card_single['rating_created_at'],
            "rated":card_single['rated'],
            "distance":card_single['distance'],
            "count_pending_request": card_single['count_pending_request']
        }
        card_post_list.append(post)

    return card_post_list


def post_master_public_response(data):
    card_post_list = list()
    for card_single in data:
        media_data = None
        if card_single['media'] != None:
            media_data = json.loads(card_single['media'])

        post = {
            "post_id":card_single['id'],
            "created_at":str(card_single['created_at']),
            "description":card_single['description'],
            "media":media_data,
            "community_id":card_single['community_id'],
            "community_name":card_single['community_name'],
            "category_id":card_single['category_id'],
            "category_name":card_single['category_name'],
            "user_id":card_single['user_id'],
            "username":card_single['username'],
            "profile_pic_url":card_single['profile_pic_url'],
            "gender":card_single['gender'],
            "designation_id":card_single['designation_id'],
            "rating":card_single['rating'],
            "ageing":card_single['ageing'],
            "lat":card_single['lat'],
            "long":card_single['long'],
            "count_like":card_single['count_like'],
            "count_comment":card_single['count_comment']
        }
        card_post_list.append(post)

    return card_post_list

def comment_master_token(**data):
    sql = """
        with
        cl as (select id,comment_id,created_at from tbl_like_comment where user_id={logged_in_user_id}),
        r as (select id,user_rated_id, rating,created_at from tbl_rating where user_id={logged_in_user_id}),
        b1 as (select id, user_id, user_blocked_id from tbl_block  where user_id={logged_in_user_id}),
        b2 as (select id, user_id, user_blocked_id from tbl_block  where user_blocked_id ={logged_in_user_id}),
        cr as (select receiver_id, count(id) as count_pending_request from tbl_chat_request where sender_id={logged_in_user_id} and is_activated isnull group by receiver_id)

        select 
        c.*,
        cl.id as comment_like_id,acl.created_at as comment_like_created_at,
        r.id as rating_id, r.rating as rated, r.created_at as rating_created_at,
        b1.id as id_block,
        b2.id as id_block_me,
        cr.count_pending_request
        from tbl_comment_master as c
        left join cl on c.id=acl.comment_id
        left join r on c.user_id=r.user_rated_id
        left join b1 on c.user_id=b1.user_blocked_id
        left join b2 on c.user_id=b2.user_id
        left join cr on c.user_id=cr.receiver_id
        where 
        b1.id isnull
        and b2.id isnull
        """.format(logged_in_user_id=data['logged_in_user_id'],logged_in_lat=data['logged_in_lat'],logged_in_long=data['logged_in_long'])
    
    return sql
    
async def update_avg_rating(user_id):
    try:
        async with in_transaction() as connection:
            sql = """
            update tbl_user set rating=r.rating
            from (select avg(rating) as rating from tbl_rating where user_rated_id={user_id}) as r
            where id = {user_id}
            """.format(user_id =user_id)
            await connection.execute_query(sql)
    except OperationalError:
        return error_response(code=400, message="something error!")