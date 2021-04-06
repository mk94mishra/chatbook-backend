from fastapi.exceptions import RequestValidationError
from fastapi import Request

from common.response import error_response


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return error_response(code=400, message="required fields cannot be empty", detail=exc.errors())
