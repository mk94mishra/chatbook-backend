from common.response import success_response, error_response
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction


async def sql_init():
    try:
        async with in_transaction() as connection:

            # create tbl_post_master
            tbl_post_master = """
            create or replace view tbl_post_master as (
            with
            al as (select post_id, count(id) as count_like from tbl_action where type='like' group by post_id),
            ac as (select post_id, count(id) as count_comment from tbl_action where type='comment' group by post_id)

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

            # create tbl_comment_master
            tbl_comment_master = """
            create or replace view tbl_comment_master as (
            with 
            ac as (select id, post_id, user_id, description, media_url, created_at from tbl_action where type='comment'),
            acl as (select count(id) as count_comment_like, comment_id from tbl_action where type='comment-like' group by comment_id)
            
            select 
            ac.*,
            u.username, u.profile_pic_url, u.rating,
            acl.count_comment_like
            from ac 
            left join tbl_user as u on ac.user_id=u.id
            left join acl on ac.id=acl.comment_id
            """
            await connection.execute_query(tbl_comment_master)
    except OperationalError:
        return error_response(code=400, message="something error!")
