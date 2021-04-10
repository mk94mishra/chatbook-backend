from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction

from common.response import error_response, success_response

from ops.action.models import Action
from ops.action.schemas import ActionCreate

router = APIRouter(prefix='/v1/private/action', tags=["action"])


# create/delete action
@router.post("/type/{action_type}", status_code=status.HTTP_201_CREATED)
async def action_post(request: Request, action_type:str, payload: ActionCreate):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data['type'] = action_type

    if action_type == 'comment':
        if (not data['description']) & (not data['media_url']):
            return error_response(code=400, message="must be set description or media!")
    if action_type == 'spam':
        if not data['description']:
            return error_response(code=400, message="must be fill description!")
    if action_type == 'block':
        if not data['user_id_blocked_id']:
            return error_response(code=400, message="must be fill user_id_blocked!")
    if action_type == 'rating':
        if (not data['user_id_rated_id']) or (not data['rating']):
            return error_response(code=400, message="must be fill user_id_rated & rating!")

    data = {k: v for k, v in data.items() if v is not None}

    if data['method'] == 'create':
        action = await Action.create(**data)
        # insert avg rating into tbl_user
        try:
            async with in_transaction() as connection:
                sql = """update tbl_user set rating=r.rating
                from (select avg(rating) as rating from tbl_action where user_id_rated_id={user_id_rated_id} and type='rating') as r
                where id = {user_id_rated_id}
                """.format(user_id_rated_id =data['user_id_rated_id'] )
                await connection.execute_query(sql)
        except OperationalError:
            return error_response(code=400, message="something error!")

        return success_response(action)

    if data['method'] == 'delete':
        # -- comment
        if action_type == 'comment':
            if (not data['comment_id']):
                return error_response(code=400, message="must be set comment_id!")

            await Action(id=data['comment_id'], is_active=False).save(update_fields=['is_active'])
            return success_response({"msg":"comment deleted"}) 
        # -- block
        if action_type == 'block':
            if not data['user_id_blocked_id']:
                return error_response(code=400, message="must be set user_id_blocked!")
            await Action.get(user_id=data['user_id'],user_id_blocked=data['user_id_blocked'],type=data['action_type']).delete()
            return success_response({"msg":"unblocked!"}) 
        # -- rating
        if action_type == 'rating':
            if not data['user_id_rated_id']:
                return error_response(code=400, message="must be set user_id_rated!")
            await Action.get(user_id=data['user_id'],user_id_blocked=data['user_id_rated_id'],type=data['action_type']).delete()
            return success_response({"msg":"un-rating deleted!"}) 

        await Action.get(user_id=data['user_id'], post_id=data['post_id'], type=data['action_type']).delete()
        return success_response({"msg":"action deleted"})

    return error_response(code=400, message="something error!")



# get block 
@router.get("/type/{action_type}/block-list", status_code=status.HTTP_200_OK)
async def user_block_list(request: Request, action_type:str, limit: Optional[int] = 10, offset: Optional[int] = 0, order_by: Optional[str] = 'b.created_at desc'):
    # self user check
    user_id = int(request.state.user_id)

    try:
        async with in_transaction() as connection:
            sql = """select b.user_id_blocked,
            u.name as username, u.profile_pic_url , b.created_at
            from tbl_action as b
            left join tbl_user as u on b.user_id_blocked = u.id"""

            where = " where b.user_id = {user_id}".format(user_id=user_id)
            
            orderby = " order by {order_by} limit {limit} offset {offset}".format(order_by=order_by, limit=limit,offset=offset)

            sql = sql + where + orderby
            blocked_user = await connection.execute_query(sql)
            
            return success_response(blocked_user[1])
    except OperationalError:
        return error_response(code=400, message="something error!")
