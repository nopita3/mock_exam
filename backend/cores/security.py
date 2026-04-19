from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends
from backend.cores.exception import InvalidToken
from backend.database.blacklist import is_jti_blacklisted
from backend.utils import decode_access_token


oauth2_scheme = HTTPBearer(auto_error=False)


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> dict:
    """ตรวจสอบ bearer token และ blacklist"""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise InvalidToken()

    data = decode_access_token(credentials.credentials)
    
    if data is None:
        raise InvalidToken()
    
    # ตรวจสอบว่า token อยู่ใน blacklist หรือไม่
    jti = data.get("jti")
    if jti and await is_jti_blacklisted(jti):
        raise InvalidToken()
    
    return data