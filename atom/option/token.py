from copy import deepcopy
from fastapi import APIRouter, Request, status

from common.response import error_response, success_response

from atom.option.models import Option
from atom.option.schemas import OptionCreate

router = APIRouter(prefix='/v1/token/option', tags=["public-option"])


# create option
@router.post("", status_code=status.HTTP_200_OK)
async def option_create(request: Request, payload: OptionCreate):
    data = deepcopy(payload.dict())
    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id
    data['is_verified'] = False
    data = {k: v for k, v in data.items() if v is not None}
    return success_response(await Option.create(**data))
    