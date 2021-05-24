from copy import deepcopy
from fastapi import APIRouter, Request, status, Depends
from tortoise.exceptions import DoesNotExist

from system.settings import settings
from common.response import error_response, success_response

from atom.action.rating.models import Rating
from atom.action.rating.schemas import RatingCreate, RatingUpdate, RatingDelete

from atom.helper.helper import update_avg_rating

router = APIRouter(prefix='/v1/token/rating', tags=["rating"])


# create rating
@router.post("", status_code=status.HTTP_201_CREATED)
async def rating_create(request: Request, payload: RatingCreate):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data = {k: v for k, v in payload.dict().items() if v is not None}

    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id
    
    await update_avg_rating(data['rated_id'])
    return success_response(await Rating.create(**data))


# update rating
@router.put("/{rating_id}", status_code=status.HTTP_201_CREATED)
async def rating_update(request: Request, rating_id: int,payload: RatingUpdate):
    data = deepcopy(payload.dict())

    rating_data = await Rating.get(id=rating_id)
    # self user check
    if rating_data.user_id != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data = {k: v for k, v in payload.dict().items() if v is not None}

    data['updated_by'] = request.state.user_id
    
    await update_avg_rating(rating_data.rated_id)
    await Rating(id=rating_id,rating=data['rating']).save(update_fields=['rating'])
    return success_response("data updated!")

# delete rating 
@router.delete("/{rating_id}", status_code=status.HTTP_201_CREATED)
async def rating_delete(request: Request,rating_id:int):

    rating_data = await Rating.get(id=rating_id)
    # self user check
    if rating_data.user_id != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    try:
        await Rating.get(rating_id=rating_id).delete()

        await update_avg_rating(rating_data.rated_id)
        return success_response({"msg":"rating deleted successfully"})
    except:
        return error_response(code=400, message="something error!")
    
