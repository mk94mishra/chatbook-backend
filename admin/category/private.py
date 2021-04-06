from copy import deepcopy
from fastapi import APIRouter, Request, status

from system.settings import settings
from common.response import error_response, success_response

from admin.category.models import Category
from admin.category.schemas import CategoryCreate

router = APIRouter(prefix='/v1/private/category', tags=["category"])


# category create
@router.post("", status_code=status.HTTP_201_CREATED)
async def category_create(request: Request, payload: CategoryCreate):
    data = deepcopy(payload.dict())
    data = {k: v for k, v in payload.dict().items() if v is not None}
    data['created_by'] = request.state.user_id
    response = await Category.create(**data)
    return success_response(response)
