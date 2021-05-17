from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction

from common.validation import form_validation, media_validation
from common.response import error_response, success_response

from atom.post.models import Post
from atom.post.schemas import PostCreate

from atom.user.models import User


router = APIRouter(prefix='/v1/token/post', tags=["post"])


# create post
@router.post("", status_code=status.HTTP_201_CREATED)
async def post_create(request: Request, payload: PostCreate):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    user = await User.get(id=data['user_id'])
    if user.community_id == None:
        return error_response(code=400, message="must be set user community!")

    data['community_id'] = user.community_id 

    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id

    if (not data['description']) & (not data['media_url']):
        return error_response(code=400, message="data is empty!")

    data['media'] = {
        'type': data['media_type'],
        'url': data['media_url'],
        'thumbnail_url': data['thumbnail_url']
    }
    ok, err = media_validation(**data['media'])
    if err:
        return error_response(code=400, message=err)

    data = {k: v for k, v in data.items() if v is not None}
    return success_response(await Post.create(**data))


# delete post 
@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def post_delete(request: Request, post_id: int):
    post = await Post.get(id=post_id)
    # self user check
    if post.user_id != request.state.user_id:
        error_response(code=401, message="you don't have permission!")
    
    data = dict()
    data['updated_by'] = request.state.user_id
    data['is_active'] = False
    data['remark'] = "by user"
    # post delete 
    await Post(id=post_id, **data).save(update_fields=data.keys())
    return success_response({"msg":"data deleted!"})
    