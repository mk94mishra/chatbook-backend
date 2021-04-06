from copy import deepcopy
from fastapi import APIRouter, Request, status

from system.settings import settings
from common.response import error_response, success_response
from admin.community.models import Community

router = APIRouter(prefix='/v1/public/community', tags=["public-community"])


# read community list all
@router.get("", status_code=status.HTTP_200_OK)
async def community_read_all():
    response = await Community.all()
    return success_response(response)

# read community list single
@router.get("/{community_id}", status_code=status.HTTP_200_OK)
async def community_read_single(community_id: int):
    response = await Community.get(id=community_id)
    return success_response(response)

