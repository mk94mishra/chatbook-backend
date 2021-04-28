from copy import deepcopy
from fastapi import APIRouter, Request, status, Depends
from tortoise.exceptions import DoesNotExist

from system.settings import settings
from common.response import error_response, success_response

from atom.action.bookmark.models import Bookmark
from atom.action.bookmark.schemas import BookmarkCreate, BookmarkDelete

router = APIRouter(prefix='/v1/token', tags=["bookmark"])


# create bookmark post
@router.post("/bookmark-post", status_code=status.HTTP_201_CREATED)
async def bookmark_post_create(request: Request, payload: BookmarkCreate):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data = {k: v for k, v in payload.dict().items() if v is not None}

    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id
    
    return success_response(await Bookmark.create(**data))

# delete bookmark post
@router.delete("/bookmark-post/post/{post_id}", status_code=status.HTTP_201_CREATED)
async def bookmark_post_delete(request: Request,post_id:int):

    user_id = int(request.state.user_id)
    try:
        await Bookmark.get(user_id=user_id, post_id=post_id).delete()
        return success_response({"msg":"post un-bookmarked successfully"})
    except:
        return error_response(code=400, message="something error!")
    
