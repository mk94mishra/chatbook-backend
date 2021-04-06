from copy import deepcopy
from fastapi import APIRouter, Request, status, Depends
from tortoise.exceptions import DoesNotExist

from system.settings import settings
from common.response import error_response, success_response

from admin.orderby.models import OrderBy

router = APIRouter(prefix='/v1/public/orderby', tags=["orderby"])


# orderby list
@router.get("", status_code=status.HTTP_201_CREATED)
async def orderby_all():
    return success_response(await OrderBy.all())