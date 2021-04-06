from fastapi import Header, HTTPException
import jwt
from time import time
from system.settings import settings



def token_create(payload):
    exp = (int(time()) + settings.TOKEN_VALIDITY_PERIOD)
    payload["exp"] = exp
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

"""def token_decode(request): 
    auth_header = request.headers.get('Authorization') 
    token = auth_header.split(" ")[1] # Parses out the "Bearer" portion
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    return payload"""

"""
async def token_verify(x_token: str = Header(...), header_user_id: str = Header(...)):
    # check token from header
    if x_token:
        token = x_token # Parses out the "Bearer" portion
    else:
        raise HTTPException(status_code=400, detail="X-Token header invalid")

    # verify token
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if (not header_user_id) or (header_user_id != int(payload['sub'])):
            raise HTTPException(status_code=400, detail="X-Token header invalid")
        
        if int(time()) > int(payload['exp']): 
            raise HTTPException(status_code=400, detail="X-Token time expired")
        
    except:
        raise HTTPException(status_code=400, detail="X-Token header invalid")
"""
    


