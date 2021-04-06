import requests
from fastapi import HTTPException, Header, Request

def same_user_permission(user_id: int, request : Request):
    print(request.headers['header-user-id'])
    header_user_id = 3
    if user_id != header_user_id:
        print("ugkgkjkj")
        raise HTTPException(status_code=400, detail="you don't have permission to update others profile")
    

"""# for same user
def same_user_permission(user_id):
    if user_id != int(Request.headers['header-user-id']):
        return {"msg":"you don't have permission to update others profile"}"""
