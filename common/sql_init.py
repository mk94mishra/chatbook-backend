from common.response import success_response, error_response
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction


async def tbl_post_master_sql_init():
    try:
        async with in_transaction() as connection:

            # create tbl_post_master
            tbl_post_master = """
            create or replace view tbl_post_master as (
            with
            al as (select post_id, count(id) as count_like from tbl_like_post group by post_id),
            ac as (select post_id, count(id) as count_comment from tbl_comment group by post_id)

            select 
            p.*,
            DATE_PART('day', AGE(CURRENT_TIMESTAMP,p.created_at)) AS ageing,
            u.username,u.gender,u.profile_pic_url,u.designation_id, u.rating, u.lat, u.long,
            ocom.name as community_name,
            ocat.name as category_name,
            al.count_like,
            ac.count_comment
            from tbl_post as p
            left join tbl_user as u on p.user_id=u.id
            left join tbl_option as ocom on p.community_id=ocom.id
            left join tbl_option as ocat on p.category_id=ocat.id
            left join al on p.id=al.post_id
            left join ac on p.id=ac.post_id
            where p.is_active=true
            )
            """
            await connection.execute_query(tbl_post_master)
            print("view 'tbl_post_master' created")
    except OperationalError:
        return error_response(code=400, message="something error!")


async def tbl_comment_master_sql_init():
    try:
        async with in_transaction() as connection:
            # create tbl_comment_master
            tbl_comment_master = """
            create or replace view tbl_comment_master as (
            with 
            ac as (select id, post_id, user_id, description, media_type,media_url, created_at from tbl_comment),
            acl as (select count(id) as count_comment_like, comment_id from tbl_like_comment group by comment_id)
            
            select 
            ac.*,
            u.username, u.profile_pic_url, u.rating,
            acl.count_comment_like
            from ac 
            left join tbl_user as u on ac.user_id=u.id
            left join acl on ac.id=acl.comment_id
            )
            """
            await connection.execute_query(tbl_comment_master)
            print("view 'tbl_comment_master' created")
    except OperationalError:
        return error_response(code=400, message="something error!")


async def tbl_chat_group_sql_init():
    try:
        async with in_transaction() as connection:
            # create tbl_chat_group1
            tbl_chat_group1 = """
            create or replace view tbl_chat_group1 as ( 
            select distinct on (group_id) group_id, 
            msg as last_msg,created_at,
            sender_id, receiver_id,
            case when (sender_id<receiver_id)  then sender_id else receiver_id end as user_id_min,
            case when (sender_id>receiver_id)  then sender_id else receiver_id end as user_id_max,
            is_seen_min, is_seen_max,
            is_deleted_min, is_deleted_max
            from tbl_chat_msg order by group_id, created_at desc
            )
            """
            await connection.execute_query(tbl_chat_group1)

            # create tbl_chat_group
            tbl_chat_group = """
            create or replace view tbl_chat_group as ( select 
            cg1.*,
            umin.username as name_min, umin.profile_pic_url as profile_pic_url_min,
            umax.username as name_max, umax.profile_pic_url as profile_pic_url_max
            from tbl_chat_group1 as cg1
            left join tbl_user as umin on cg1.user_id_min=umin.id
            left join tbl_user as umax on cg1.user_id_max=umax.id
            )
            """
            await connection.execute_query(tbl_chat_group)
            print("view 'tbl_chat_group' created")
    except OperationalError:
        return error_response(code=400, message="something error!")
