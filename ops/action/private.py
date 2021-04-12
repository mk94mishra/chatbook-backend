from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction

from common.response import error_response, success_response
from admin.helper.helper.py import update_avg_rating

from ops.action.models import Action
from ops.action.schemas import ActionCreate

router = APIRouter(prefix='/v1/private/action', tags=["action"])


# create action
@router.post("/type/{action_type}", status_code=status.HTTP_201_CREATED)
async def action_post_create(request: Request, action_type:str, payload: ActionCreate):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data['type'] = action_type

    if action_type == 'like':
        if (not data['post_id']):
            return error_response(code=400, message="must be set post_id!")
    if action_type == 'comment':
        if (not data['post_id']) & ((not data['description']) or (not data['media_url'])):
            return error_response(code=400, message="must be set post_id, description or media!")
    if action_type == 'bookmark':
        if (not data['post_id']):
            return error_response(code=400, message="must be set post_id!")
    if action_type == 'spam':
        if (not data['post_id']) & (not data['description']):
            return error_response(code=400, message="must be set post_id & description!")
    if action_type == 'block':
        if not data['user_id_blocked_id']:
            return error_response(code=400, message="must be fill user_id_blocked!")
    if action_type == 'rating':
        if (not data['user_id_rated_id']) & (not data['rating']):
            return error_response(code=400, message="must be fill user_id_rated & rating!")

    data = {k: v for k, v in data.items() if v is not None}
    action = await Action.create(**data)

    # insert avg rating into tbl_user
    if action_type == 'rating':
        update_avg_rating(data['user_id_rated_id'])

    return success_response(action)


# delete action
@router.delete("/{action_id}", status_code=status.HTTP_200_OK)
async def action_delete(request: Request,action_id:int):
    # self user check
    user_id = int(request.state.user_id)
    await Action.get(id=action_id, user_id=user_id).delete()
    return success_response({"msg":"action deleted!"})



# get block 
@router.get("/type/{action_type}/block-list", status_code=status.HTTP_200_OK)
async def user_block_list(request: Request, action_type:str, limit: Optional[int] = 10, offset: Optional[int] = 0):
    # self user check
    user_id = int(request.state.user_id)

    try:
        async with in_transaction() as connection:
            sql = """select ab.id as action_id_block, ab.user_id_blocked, ab.created_at,
            u.name as username, u.profile_pic_url
            from tbl_action as ab
            left join tbl_user as u on ab.user_id_blocked = u.id"""

            where = " where ab.user_id = {user_id}".format(user_id=user_id)
            orderby = " order by ab.created_at desc limit {limit} offset {offset}".format(limit=limit,offset=offset)

            sql = sql + where + orderby
            blocked_user = await connection.execute_query(sql)            
            return success_response(blocked_user[1])
    except OperationalError:
        return error_response(code=400, message="something error!")
