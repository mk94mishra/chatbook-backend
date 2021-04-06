from copy import deepcopy
from fastapi import APIRouter, Request, status

from common.response import error_response, success_response

from admin.faq.models import Faq

router = APIRouter(prefix='/v1/public/faq', tags=["Faq"])



# faq get
@router.get("", status_code=status.HTTP_200_OK)
async def faq_all():
    return success_response(await Faq.all())


