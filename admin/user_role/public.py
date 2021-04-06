from copy import deepcopy
from fastapi import APIRouter, Request, status

from system.settings import settings
from common.response import error_response, success_response
from admin.user_role.models import UserRole

router = APIRouter(prefix='/v1/public/user-role', tags=["public-user-role"])


# read user role list all
@router.get("", status_code=status.HTTP_200_OK)
async def role_read_all():
    response = await UserRole.all()
    return success_response(response)

# read user role list single
@router.get("/{role_id}", status_code=status.HTTP_200_OK)
async def role_read_single(role_id: int):
    response = await UserRole.get(id=role_id)
    return success_response(response)

