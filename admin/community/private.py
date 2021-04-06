from copy import deepcopy
from fastapi import APIRouter, Request, status

from system.settings import settings
from common.response import error_response, success_response

from admin.community.models import Community
from admin.community.schemas import CommunityCreate, CommunityUpdate

router = APIRouter(prefix='/v1/private/community', tags=["community"])


# community create
@router.post("", status_code=status.HTTP_201_CREATED)
async def community_create(request: Request, payload: CommunityCreate):
    data = deepcopy(payload.dict())
    data = {k: v for k, v in payload.dict().items() if v is not None}
    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id
    response = await Community.create(**data)
    return success_response(response)

# community create
@router.put("/{community_id}", status_code=status.HTTP_200_OK)
async def community_update(request: Request,community_id:int, payload: CommunityUpdate):
    data = deepcopy(payload.dict())
    data = {k: v for k, v in payload.dict().items() if v is not None}
    data['updated_by'] = request.state.user_id
    # update data
    response = await Community(id=community_id, **data).save(update_fields=data.keys())
    return success_response(response)
