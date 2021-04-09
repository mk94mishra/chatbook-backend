1. tbl_option
ALTER TABLE tbl_option  
   ADD CONSTRAINT check_types 
   CHECK ("type" IN ('community','category','designation') )

1.a. tbl_action
ALTER TABLE tbl_action  
   ADD CONSTRAINT check_types 
   CHECK ("type" IN ('like','bookmark','spam','comment','block') )

2. chat group1 tbl as view

create view tbl_chat_group1 as ( 
select distinct on (group_id) group_id, 
msg as last_msg,created_at,
sender_id, receiver_id,
case when (sender_id<receiver_id)  then sender_id else receiver_id end as user_id_min,
case when (sender_id>receiver_id)  then sender_id else receiver_id end as user_id_max,
is_seen_min, is_seen_max,
is_deleted_min, is_deleted_max
from tbl_chat_msg order by group_id, created_at desc
)


3. chat group with user profile

create view tbl_chat_group as ( select 
cg1.*,
 umin.username as name_min, umin.profile_pic_url as profile_pic_url_min,
 umax.username as name_max, umax.profile_pic_url as profile_pic_url_max
from tbl_chat_group1 as cg1
left join tbl_user as umin on cg1.user_id_min=umin.id
left join tbl_user as umax on cg1.user_id_max=umax.id
)


4. chat user

select
user_id_max as user_id, profile_pic_url_max as profile_pic_url, name_max as "name", last_msg, is_seen_min as is_seen, created_at
from tbl_chat_group where user_id_min=5 
union 
select
user_id_min as user_id, profile_pic_url_min as profile_pic_url, name_min as "name", last_msg, is_seen_max as is_seen, created_at
from tbl_chat_group where user_id_max=5 


5. tbl_card_user

create or replace view tbl_card_user as (
select 
u.*, 
oc.name as community_name,
od.name as designation_name
from tbl_user as u
left join tbl_option as oc on u.community_id = oc.id 
left join tbl_option as od on u.designation_id =od.id
where u.is_active=true
)

  
6. tbl_card_post

create or replace view tbl_card_post as (
with
lp as (select post_id, count(id) as count_like from tbl_action where type='like' group by post_id),
cp as (select post_id, count(id) as count_comment from tbl_action where type='comment' group by post_id)
select 
p.*,
(DATE_PART('day', AGE(CURRENT_TIMESTAMP,p.created_at))) AS ageing,
ocat.name as category_name,
ocom.name as community_name,
u.username as username,u.gender as gender,u.profile_pic_url,u.designation_id, u.lat, u.long,
lp.count_like,
cp.count_comment
from tbl_post as p
left join tbl_option as ocat on p.category_id = ocat.id
left join tbl_option as ocom on p.community_id = ocom.id
left join tbl_user as u on p.user_id = u.id
left join lp on p.id = lp.post_id
left join cp on p.id=cp.post_id
where p.is_active=true
)


7. tbl_card_post_private
with
lpu as (select lpu.post_id, lpu.created_at, true as is_like from tbl_action as lpu where lpu.type='like' and lpu.user_id=1),   
bpu as (select bu.post_id, bu.created_at, true as is_bookmark from tbl_action as bu where bu.type='bookmark' and bu.user_id=1),            cpu as (select c.post_id, max(c.created_at) as created_at, true as is_comment from tbl_action as c where c.type='comment' and c.user_id=1 group by c.post_id),
ub as (select ub1.user_id_blocked_id  as user_id, true as is_block from tbl_action as ub1  where ub1.user_id=1 and ub1.type='block' union select ub2.user_id  as user_id, true as is_block from tbl_action as ub2 where ub2.user_id_blocked_id=1 and ub2.type='block')
select
p.*,
lpu.is_like,
bpu.is_bookmark,
cpu.is_comment,
ub.is_block,
st_distance(st_makepoint(p.lat,p.long), st_makepoint(-60437559.76521781,75051467.17286935)) as distance
from tbl_card_post as p
left join lpu on p.id=lpu.post_id
left join bpu on p.id=bpu.post_id
left join cpu on p.id=cpu.post_id
left join ub on p.user_id=ub.user_id
where ub.is_block isnull and lower(p.description) LIKE '%aute officia%' order by p.created_at desc nulls last limit 10 offset 
0

9. tbl_card_comment

create view tbl_card_comment as (
    select 
    c.*,
    u.username as username, u.profile_pic_url 
    from tbl_action as c
    left join tbl_user as u on c.user_id = u.id
    where c.type='comment'
)

