from copy import deepcopy
from fastapi import APIRouter, Request, status

from system.settings import settings
from common.response import error_response, success_response

from admin.user_type.models import UserType
from admin.user_type.schemas import UserTypeCreate

router = APIRouter(prefix='/v1/public/user-type', tags=["public-user-type"])

# usertype read list
@router.get("", status_code=status.HTTP_200_OK)
async def usertype_read_all():
    response  = await UserType.all()
    return success_response(response)


# usertype read 
@router.get("/{usertype_id}", status_code=status.HTTP_200_OK)
async def usertype_read_single(usertype_id:int):
    response = await UserType.get(id=usertype_id)
    return success_response(response)