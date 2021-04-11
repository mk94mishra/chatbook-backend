import json


def card_post_private(logged_in_user,logged_in_lat,logged_in_long,community_id):
    sql = """
        with
        al as (select id,post_id,created_at from tbl_action where type='like' and user_id={logged_in_user}),
        ac as (select array_agg(id) as id, post_id, max(created_at) as created_atfrom tbl_action where type='comment' and user_id={logged_in_user} group by post_id),
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
        ab2.id as action_id_block_me
        st_distance(st_makepoint(p.lat,p.long), st_makepoint({logged_in_lat},{logged_in_long})) as distance
        from tbl_card_post as p
        left join al on p.id=al.post_id
        left join ac on p.id=ac.post_id
        left join abo on p.id=abo.post_id
        left join asp on p.id=asp.post_id
        left join ab1 on p.user_id=ab1.user_id_blocked_id
        left join ab2 on p.user_id=ab2.user_id
        where is_active=true 
        and action_id_block isnull 
        and action_id_block_me isnull 
        and community_id={community_id}""".format(logged_in_user=logged_in_user,logged_in_lat=logged_in_lat,logged_in_long=logged_in_long,community_id=community_id)
    
    return sql


def card_post_private_response(card_post):
    card_post_list = list()
    for card_single in card_post:
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