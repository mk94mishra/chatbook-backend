from copy import deepcopy
from fastapi import APIRouter, Request, status, Depends
from tortoise.exceptions import DoesNotExist

from system.settings import settings
from common.response import error_response, success_response

from atom.action.like.models import LikePost, LikeComment
from atom.action.like.schemas import LikePostCreate, LikeCommentCreate

router = APIRouter(prefix='/v1/token', tags=["like"])


# create like post
@router.post("/like-post", status_code=status.HTTP_201_CREATED)
async def like_post_create(request: Request, payload: LikePostCreate):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data = {k: v for k, v in payload.dict().items() if v is not None}

    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id
    
    return success_response(await LikePost.create(**data))

# delete like post
@router.delete("/like-post/post/{post_id}", status_code=status.HTTP_201_CREATED)
async def like_post_delete(request: Request,post_id:int):
    # self user check
    user_id = int(request.state.user_id)
    try:
        await LikePost.get(user_id=user_id, post_id=post_id).delete()
        return success_response({"msg":"post dislike successfully"})
    except:
        return error_response(code=400, message="something error!")
    

# create like comment
@router.post("/like-comment", status_code=status.HTTP_201_CREATED)
async def like_comment_create(request: Request, payload: LikeCommentCreate):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data = {k: v for k, v in payload.dict().items() if v is not None}

    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id
    
    return success_response(await LikeComment.create(**data))

# delete like post
@router.delete("/like-comment/comment/{comment_id}", status_code=status.HTTP_201_CREATED)
async def like_comment_delete(request: Request, comment_id:int):

    user_id = int(request.state.user_id)
    try:
        await LikeComment.get(user_id=user_id, comment_id=comment_id).delete()
        return success_response({"msg":"comment dislike successfully"})
    except:
        return error_response(code=400, message="something error!")