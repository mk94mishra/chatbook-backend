import json
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction

from common.response import error_response, success_response

def post_master_token(**data):
    sql = """
        with
        al as (select id,post_id,created_at from tbl_like_post where user_id={logged_in_user}),
        ac as (select array_agg(id) as id, post_id, max(created_at) as created_at from tbl_comment where user_id={logged_in_user} group by post_id),
        abo as (select id,post_id ,created_at from tbl_bookmark where user_id={logged_in_user}),
        asp as (select id,post_id ,created_at from tbl_spam where user_id={logged_in_user}),
        ar as (select id,rated_id, rating,created_at from tbl_rating where user_id={logged_in_user}),
        ab1 as (select id, user_id, user_blocked_id from tbl_block  where user_id={logged_in_user}),
        ab2 as (select id, user_id, user_blocked_id from tbl_block where user_blocked_id ={logged_in_user}),
        cr as (select receiver_id, count(id) as count_pending_request from tbl_chat_request where sender_id={logged_in_user} and is_activated isnull group by receiver_id)

        select 
        p.*,
        al.id as action_like_id,al.created_at as action_like_created_at,
        ac.id as action_comment_id,ac.created_at as action_comment_created_at,
        abo.id as action_bookmark_id,abo.created_at as action_bookmark_created_at,
        asp.id as action_spam_id, asp.created_at as action_spam_created_at,
        ar.id as action_rating_id, ar.rating as action_rated, ar.created_at as action_rating_created_at,
        ab1.id as action_id_block,
        ab2.id as action_id_block_me,
        st_distance(st_makepoint(p.lat,p.long), st_makepoint({logged_in_lat},{logged_in_long})) as distance,
        cr.count_pending_request
        from tbl_post_master as p
        left join al on p.id=al.post_id
        left join ac on p.id=ac.post_id
        left join abo on p.id=abo.post_id
        left join asp on p.id=asp.post_id
        left join ar on p.user_id=ar.rated_id
        left join ab1 on p.user_id=ab1.user_blocked_id
        left join ab2 on p.user_id=ab2.user_id
        left join cr on p.user_id=cr.receiver_id
        where is_active=true 
        and ab1.id isnull
        and ab2.id isnull
        """.format(logged_in_user=data['logged_in_user'],logged_in_lat=data['logged_in_lat'],logged_in_long=data['logged_in_long'])
    
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

            "action_like_id":card_single['action_like_id'],
            "action_like_created_at":card_single['action_like_created_at'],
            "action_comment_id":card_single['action_comment_id'],
            "action_comment_created_at":card_single['action_comment_created_at'],
            "action_bookmark_id":card_single['action_bookmark_id'],
            "action_bookmark_created_at":card_single['action_bookmark_created_at'],
            "action_spam_id":card_single['action_spam_id'],
            "action_spam_created_at":card_single['action_spam_created_at'],
            "action_rating_id":card_single['action_rating_id'],
            "action_rating_created_at":card_single['action_rating_created_at'],
            "action_rated":card_single['action_rated'],
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
        acl as (select id,comment_id,created_at from tbl_like_comment where user_id={logged_in_user}),
        ar as (select id,rated_id, rating,created_at from tbl_rating where user_id={logged_in_user}),
        ab1 as (select id, user_id, user_blocked_id from tbl_block  where user_id={logged_in_user}),
        ab2 as (select id, user_id, user_blocked_id from tbl_block  where user_blocked_id ={logged_in_user}),
        cr as (select receiver_id, count(id) as count_pending_request from tbl_chat_request where sender_id={logged_in_user} and is_activated isnull group by receiver_id)

        select 
        c.*,
        acl.id as action_comment_like_id,acl.created_at as action_comment_like_created_at,
        ar.id as action_rating_id, ar.rating as action_rated, ar.created_at as action_rating_created_at,
        ab1.id as action_id_block,
        ab2.id as action_id_block_me,
        cr.count_pending_request
        from tbl_comment_master as c
        left join acl on c.id=acl.comment_id
        left join ar on c.user_id=ar.rated_id
        left join ab1 on c.user_id=ab1.user_blocked_id
        left join ab2 on c.user_id=ab2.user_id
        left join cr on c.user_id=cr.receiver_id
        where 
        ab1.id isnull
        and ab2.id isnull
        """.format(logged_in_user=data['logged_in_user'],logged_in_lat=data['logged_in_lat'],logged_in_long=data['logged_in_long'])
    
    return sql
    
async def update_avg_rating(user_id):
    try:
        async with in_transaction() as connection:
            sql = """
            update tbl_user set rating=r.rating
            from (select avg(rating) as rating from tbl_rating where rated_id={user_id}) as r
            where id = {user_id}
            """.format(user_id =user_id)
            await connection.execute_query(sql)
    except OperationalError:
        return error_response(code=400, message="something error!")