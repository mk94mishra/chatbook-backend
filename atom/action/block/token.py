from copy import deepcopy
from typing import Optional
from fastapi import APIRouter, Request, status, Depends
from tortoise.exceptions import DoesNotExist

from system.settings import settings
from common.response import error_response, success_response

from atom.action.block.models import Block
from atom.action.block.schemas import BlockCreate, BlockDelete

router = APIRouter(prefix='/v1/token/block', tags=["block"])


# create block
@router.post("", status_code=status.HTTP_201_CREATED)
async def block_create(request: Request, payload: BlockCreate):
    data = deepcopy(payload.dict())

    # self user check
    if int(data['user_id']) != int(request.state.user_id):
        return error_response(code=400, message="you don't have permision!")

    data = {k: v for k, v in payload.dict().items() if v is not None}

    data['created_by'] = request.state.user_id
    data['updated_by'] = request.state.user_id
    
    return success_response(await Block.create(**data))

# get block 
@router.get("/block-list", status_code=status.HTTP_200_OK)
async def user_block_list(request: Request, limit: Optional[int] = 10, offset: Optional[int] = 0):
    # self user check
    logged_user_id = int(request.state.user_id)
    try:
        async with in_transaction() as connection:
            sql = """
            with 
            ab as (select id, created_at, blocked_id from tbl_block where user_id={logged_user_id})

            select
            ab.id, ab.blocked_id, ab.created_at ,
            u.username,u.profile_pic_url
            from ab
            left join tbl_user as u on ab.blocked_id=u.id
            """.format(logged_user_id=logged_user_id)

            orderby = " order by ab.created_at desc limit {limit} offset {offset}".format(limit=limit,offset=offset)

            sql = sql + orderby
            blocked_user = await connection.execute_query(sql)            
            return success_response(blocked_user[1])
    except OperationalError:
        return error_response(code=400, message="something error!")


# delete block 
@router.delete("/block/{blocked_id}", status_code=status.HTTP_201_CREATED)
async def block_delete(request: Request,blocked_id:int):

    user_id = int(request.state.user_id)
    try:
        await Block.get(user_id=user_id, blocked_id=blocked_id).delete()
        return success_response({"msg":"block deleted successfully"})
    except:
        return error_response(code=400, message="something error!")
    
