from copy import deepcopy
from fastapi import APIRouter, Request, status

from system.settings import settings
from common.response import error_response, success_response
from admin.category.models import Category

router = APIRouter(prefix='/v1/public/category', tags=["public-category"])


# read category list all
@router.get("", status_code=status.HTTP_200_OK)
async def category_read_all():
    response = await Category.all()
    return success_response(response)

# read role list single
@router.get("/{category_id}", status_code=status.HTTP_200_OK)
async def category_read_single(category_id: int):
    response = await Category.get(id=category_id)
    return success_response(response)

