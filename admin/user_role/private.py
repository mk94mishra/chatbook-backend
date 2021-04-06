from copy import deepcopy
from fastapi import APIRouter, Request, status

from system.settings import settings
from common.response import error_response, success_response

from admin.user_role.models import UserRole
from admin.user_role.schemas import UserRoleCreate

router = APIRouter(prefix='/v1/private/user-role', tags=["role"])


# role create
@router.post("", status_code=status.HTTP_201_CREATED)
async def role_create(request: Request, payload: UserRoleCreate):
    data = deepcopy(payload.dict())
    data = {k: v for k, v in payload.dict().items() if v is not None}
    data['created_by'] = request.state.user_id
    response = await UserRole.create(**data)
    return success_response(response)
