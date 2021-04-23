from copy import deepcopy
from fastapi import APIRouter, Request, status

from common.response import error_response, success_response

from atom.option.models import Option

router = APIRouter(prefix='/v1/public/option', tags=["public-option"])


# get option
@router.get("/type/{type_name}", status_code=status.HTTP_200_OK)
async def option_all(type_name:str):
    option = await Option.filter(type=type_name)
    return success_response(option)
    