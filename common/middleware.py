import jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from fastapi import Header, HTTPException

from system.settings import settings
from common.response import error_response

from atom.user.models import User


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, dispatch=None, exclude=()):
        super().__init__(app=app, dispatch=dispatch)
        self.exclude = exclude

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if any(url for url in self.exclude if request.url.path.startswith(url)):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
    
        header_split = auth_header.split(" ")
        if len(header_split) == 2:
            if header_split[0].lower() != "bearer":
                return error_response(code=401, message="invalid token")

            token = header_split[1]
            try:
                claims = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                request.state.__setattr__("user_id", claims.get('sub', ''))
                user = await User.get(id=request.state.user_id)
                if user.is_active == False:
                     return error_response(code=401, message="token error!")
                """user = await User.get(id=request.state.user_id)
                # self user check
                if (user.is_active == False) or (user.is_deleted == True):
                    return error_response(code=400, message="you don't have permision!")"""

                return await call_next(request)
            except Exception as e:
                return error_response(code=401, message=str(e))
        else:
            return error_response(code=401, message="unauthorized request")