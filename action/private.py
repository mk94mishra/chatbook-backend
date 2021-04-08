from copy import deepcopy
from fastapi import APIRouter, Request, status
from tortoise.exceptions import DoesNotExist

from common.response import error_response, success_response

from home.action.models import ActionPost
from home.action.schemas import ActionCreate

router = APIRouter(prefix='/v1/private/action-home', tags=["action-home"])


# create/delete action
@router.post("/type/{action_type}", status_code=status.HTTP_201_CREATED)
async def action_home(request: Request, action_type:str, payload: ActionCreate):
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
        if not data['user_id_blocked']:
            return error_response(code=400, message="must be fill user_id_blocked!")


    data = {k: v for k, v in data.items() if v is not None}

    if data['method'] == 'create':
        return success_response(await ActionPost.create(**data))
    if data['method'] == 'delete':
        await ActionPost.get(user_id=data['user_id'], post_id=data['post_id'], type=data['action_type']).delete()
        return success_response({"msg":"action deleted"})

    return error_response(code=400, message="something error!")

