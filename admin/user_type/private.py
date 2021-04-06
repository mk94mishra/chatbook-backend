from copy import deepcopy
from fastapi import APIRouter, Request, status

from system.settings import settings
from common.response import error_response, success_response

from admin.user_type.models import UserType
from admin.user_type.schemas import UserTypeCreate

router = APIRouter(prefix='/v1/private/user-type', tags=["user-type"])


# usertype create
@router.post("", status_code=status.HTTP_201_CREATED)
async def usertype_create(request: Request, payload: UserTypeCreate):
    data = deepcopy(payload.dict())
    data = {k: v for k, v in payload.dict().items() if v is not None}
    data['created_by'] = request.state.user_id
    response = await UserType.create(**data)
    return success_response(response)
