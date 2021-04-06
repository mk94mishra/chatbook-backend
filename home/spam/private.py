from copy import deepcopy
from fastapi import APIRouter, Request, status, Depends
from tortoise.exceptions import DoesNotExist

from system.settings import settings
from common.response import error_response, success_response

from home.spam.models import Spam
from home.spam.schemas import SpamCreate

router = APIRouter(prefix='/v1/private', tags=["spam"])


# create spam post
@router.post("/spam-post", status_code=status.HTTP_201_CREATED)
async def spam_post_create(request: Request, payload: SpamCreate):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data = {k: v for k, v in payload.dict().items() if v is not None}

    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id
    
    return success_response(await Spam.create(**data))
