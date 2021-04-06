from copy import deepcopy
from fastapi import APIRouter, Request, status

from system.settings import settings
from common.response import error_response, success_response

from admin.official.models import Official
from admin.official.schemas import OfficialCreate

router = APIRouter(prefix='/v1/private/official', tags=["Official"])


# official create
@router.post("", status_code=status.HTTP_201_CREATED)
async def official_create(request: Request, payload: OfficialCreate):
    data = deepcopy(payload.dict())
    data = {k: v for k, v in payload.dict().items() if v is not None}
    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id
    response = await Official.create(**data)
    return success_response(response)


# official get
@router.get("", status_code=status.HTTP_200_OK)
async def official_all():
    return success_response(await Official.all())


