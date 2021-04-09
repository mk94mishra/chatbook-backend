from copy import deepcopy
from fastapi import APIRouter, Request, status
import datetime
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.transactions import in_transaction

from common.response import error_response, success_response

from ops.rating.models import Rating
from ops.rating.schemas import RatingCreate

router = APIRouter(prefix='/v1/private/rating', tags=["rating"])


# rating create
@router.put("", status_code=status.HTTP_201_CREATED)
async def rating_create(request: Request, payload: RatingCreate):
    data = deepcopy(payload.dict())
    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=401, message="you don't have permission!")
    
    data = {k: v for k, v in payload.dict().items() if v is not None}
    if (data['rating'] < 0) or  (data['rating'] > 10):
         return error_response(code=400, message="rating between 0 to 10!")
    try:
        data['updated_at'] = datetime.datetime.now()
        rating = await Rating.get(user_id=data['user_id'], user_id_rated=data['user_id_rated_id'])
        await Rating(id=rating.id, **data).save(update_fields=data.keys())
    except:
        await Rating.create(**data)

    try:
        async with in_transaction() as connection:
            sql = """
            UPDATE
                tbl_user
            SET
                rating = r.rating
            FROM
                (select avg(rating) as rating from tbl_rating where user_id_rated_id = {user_id_rated_id} group by user_id_rated_id) as r
            WHERE
                id = {user_id_rated_id}""".format(user_id_rated_id=data['user_id_rated_id'])

            await connection.execute_query(sql)
            print(sql)
            return success_response(data)
    except OperationalError:
        return error_response(code=400, message="something error!")

