from copy import deepcopy
from fastapi import APIRouter, Request, status

from system.settings import settings
from common.response import error_response, success_response

from admin.official.models import Official

router = APIRouter(prefix='/v1/public/official', tags=["Official"])


# official get
@router.get("", status_code=status.HTTP_200_OK)
async def official_all():
    return success_response(await Official.all())


