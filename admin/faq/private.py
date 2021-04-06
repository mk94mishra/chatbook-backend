from copy import deepcopy
from fastapi import APIRouter, Request, status

from system.settings import settings
from common.response import error_response, success_response

from admin.faq.models import Faq
from admin.faq.schemas import FaqCreate

router = APIRouter(prefix='/v1/private/faq', tags=["Faq"])


# faq create
@router.post("", status_code=status.HTTP_201_CREATED)
async def faq_create(request: Request, payload: FaqCreate):
    data = deepcopy(payload.dict())
    data = {k: v for k, v in payload.dict().items() if v is not None}
    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id
    response = await Faq.create(**data)
    return success_response(response)


# faq get
@router.get("", status_code=status.HTTP_200_OK)
async def faq_all():
    return success_response(await Faq.all())


