
def card_post_private(logged_in_user,logged_in_lat,logged_in_long):
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
        where is_active=true and action_id_block isnull and action_id_block_me isnull """.formate(logged_in_user=logged_in_user,logged_in_lat=logged_in_lat,logged_in_long=logged_in_long)
    
    return sql
