from copy import deepcopy
from fastapi import APIRouter, Request, status, Depends, HTTPException
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction
from typing import Optional
from uuid import uuid4

from system.settings import settings
from common.response import error_response, success_response

from atom.action.comment.models import Comment
from atom.action.comment.schemas import CommentCreate, CommentUpdate


router = APIRouter(prefix='/v1/token/comment', tags=["comment"])


# create comment for post
@router.post("", status_code=status.HTTP_201_CREATED)
async def comment_create(request: Request, payload: CommentCreate):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")
    
    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id
    
    if (not data['description']) & (not data['media_url']):
        return error_response(code=400, message="data is empty!")
    if data['media_url']:
        data['media_type'] = "image"
    
    data = {k: v for k, v in data.items() if v is not None}
    comment = await Comment.create(**data)
    return success_response(comment)



# delete comment
@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
async def comment_delete(request: Request, comment_id: int):
    comment = await Comment.get(id=comment_id)
    if comment.user_id != request.state.user_id:
        return error_response(code=400, message="you don't have permision!")

    await Comment.get(id=comment_id).delete()
    return success_response({"msg":"comment deleted"})