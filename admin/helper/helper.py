import json
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction

from common.response import error_response, success_response

def card_post_private(**data):
    sql = """
        with
        al as (select id,post_id,created_at from tbl_action where type='like' and user_id={logged_in_user}),
        ac as (select array_agg(id) as id, post_id, max(created_at) as created_at from tbl_action where type='comment' and user_id={logged_in_user} group by post_id),
        abo as (select id,post_id ,created_at from tbl_action where type='bookmark' and user_id={logged_in_user}),
        asp as (select id,post_id ,created_at from tbl_action where type='spam' and user_id={logged_in_user}),
        ab1 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id={logged_in_user}),
        ab2 as (select id, user_id, user_id_blocked_id from tbl_action  where type='block' and user_id_blocked_id ={logged_in_user})
        cr as (select receiver_id, count(id) as count_pending_request from tbl_chat_request where user_id={logged_in_user} and is_activated isnull group by receiver_id)

        select 
        p.*,
        al.id as action_id_like,al.created_at as created_at_like,
        ac.id as action_id_comment,ac.created_at as created_at_comment,
        abo.id as action_id_bookmark,abo.created_at as created_at_bookmark,
        asp.id as action_id_spam, asp.created_at as created_at_spam,
        ab1.id as action_id_block,
        ab2.id as action_id_block_me,
        st_distance(st_makepoint(p.lat,p.long), st_makepoint({logged_in_lat},{logged_in_long})) as distance,
        cr.count_pending_request
        from tbl_card_post as p
        left join al on p.id=al.post_id
        left join ac on p.id=ac.post_id
        left join abo on p.id=abo.post_id
        left join asp on p.id=asp.post_id
        left join ab1 on p.user_id=ab1.user_id_blocked_id
        left join ab2 on p.user_id=ab2.user_id
        left join cr on p.user_id=cr.receiver_id
        where is_active=true 
        and ab1.id isnull
        and ab2.id isnull
        """.format(logged_in_user=data['logged_in_user'],logged_in_lat=data['logged_in_lat'],logged_in_long=data['logged_in_long'])
    
    return sql


def card_post_private_response(data):
    card_post_list = list()
    for card_single in data:
        media_data = None
        if card_single['media'] != None:
            media_data = json.loads(card_single['media'])

        post = {
            "post_id":card_single['id'],
            "created_at":card_single['created_at'],
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

            "action_id_like":card_single['action_id_like'],
            "created_at_like":card_single['created_at_like'],
            "action_id_comment":card_single['action_id_comment'],
            "created_at_comment":card_single['created_at_comment'],
            "action_id_bookmark":card_single['action_id_bookmark'],
            "created_at_bookmark":card_single['created_at_bookmark'],
            "action_id_spam":card_single['action_id_spam'],
            "created_at_spam":card_single['created_at_spam'],
            "distance":card_single['distance'],
            "count_pending_request": card_single['count_pending_request']
        }
        card_post_list.append(post)

    return card_post_list


def card_post_public_response(data):
    card_post_list = list()
    for card_single in data:
        media_data = None
        if card_single['media'] != None:
            media_data = json.loads(card_single['media'])

        post = {
            "post_id":card_single['id'],
            "created_at":card_single['created_at'],
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


def update_avg_rating(user_id):
    try:
        with in_transaction() as connection:
            sql = """update tbl_user set rating=r.rating
            from (select avg(rating) as rating from tbl_action where user_id_rated_id={user_id} and type='rating') as r
            where id = {user_id}
            """.format(user_id =user_id)
            connection.execute_query(sql)
    except OperationalError:
        return error_response(code=400, message="something error!")