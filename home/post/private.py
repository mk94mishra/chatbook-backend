from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, HTTPException, Depends
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction
from system.settings import settings

from common.validation import form_validation
from common.response import error_response, success_response

from home.post.models import Post
from home.post.schemas import PostCreate, PostUpdate

from user.models import User


router = APIRouter(prefix='/v1/private/post', tags=["post"])


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

    if not data['media_url']:
        data['media_type'] = None
        data['thumbnail_url'] = None

    if data['media_url']:
        if (not data['media_type']):
            return error_response(code=400, message="must be set media type!")

    if data['media_type'] == 'video':
        if len(data['thumbnail_url']) != len(data['media_url']):
            return error_response(code=400, message="must be set thumbnail!")
        if len(data['media_url']) > 1:
            return error_response(code=400, message="maximum one video upload!")

    if data['media_type'] == 'image':
        data['thumbnail_url'] = None
        if len(data['media_url']) > 5:
            return error_response(code=400, message="maximum five image upload!")

    if data['media_type'] == 'pdf':
        if len(data['media_url']) > 1:
            return error_response(code=400, message="maximum one pdf upload!")

    if data['media_type'] == 'image' or data['media_type'] == 'video' or data['media_type'] == 'pdf' or  data['media_type'] == None:

        if data['media_type']:
            for m_url in data['media_url']:
                ok, err = form_validation('url', m_url)
                if err:
                    return error_response(code=400, message=err)
            
            if data['media_type'] == 'video':
                for t_url in data['thumbnail_url']:
                    ok, err = form_validation('url', t_url)
                    if err:
                        return error_response(code=400, message=err)

            data['media'] = {
                'type': data['media_type'],
                'url': data['media_url'],
                'thumbnail_url': data['thumbnail_url']
            }
        data = {k: v for k, v in data.items() if v is not None}
        return success_response(await Post.create(**data))

    return error_response(code=400, message="something error!")


# update post 
@router.put("/{post_id}", status_code=status.HTTP_201_CREATED)
async def post_update(request: Request, post_id: int, payload: PostUpdate):
    data = deepcopy(payload.dict())
    post = await Post.get(id=post_id)

    # self user check
    if post.user_id != request.state.user_id:
        error_response(code=401, message="you don't have permission!")

    data['updated_by'] = request.state.user_id
    
    # media update
    if len(data['media_url']):
        if not data['media_type']:
            return error_response(code=400, message="must be set media type!")

    if data['media_type'] == 'video':
        if len(data['thumbnail_url']) != len(data['media_url']):
            return error_response(code=400, message="must be set thumbnail!")
        if len(data['media_url']) > 1:
            return error_response(code=400, message="maximum one video upload!")
    
    if data['media_type'] == 'image':
        data['thumbnail_url'] = None
        if len(data['media_url']) > 5:
            return error_response(code=400, message="maximum five image upload!")
    
    if data['media_type'] == 'pdf':
        if len(data['media_url']) > 1:
            return error_response(code=400, message="maximum one pdf upload!")
    
    if data['media_type'] == 'image' or data['media_type'] == 'video' or data['media_type'] == 'pdf' or  data['media_type'] == None:

        data['media'] = None
        if data['media_type']:
            data['media'] = {
                'type': data['media_type'],
                'url': data['media_url'],
                'thumbnail_url': data['thumbnail_url']
            }

        post_data = {
            "description": data["description"],
            "media": data['media']
        }
    
        # post update 
        await Post(id=post_id, **post_data).save(update_fields=post_data.keys())
        return success_response({"msg":"data updated!"})


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
    data['is_deleted'] = True
    # post delete 
    await Post(id=post_id, **data).save(update_fields=data.keys())
    return success_response({"msg":"data deleted!"})
    