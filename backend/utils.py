from datetime import datetime, timedelta, timezone
from uuid import uuid4
from pathlib import Path

from fastapi import HTTPException, status
import jwt
from backend.config import securuity_settings
from backend.cores.exception import InvalidToken

def generate_access_token(data:dict , 
                          expiry: timedelta = timedelta(days=14)
                          ) -> str:
    
    token = jwt.encode(payload={**data,
                                "jti":str(uuid4()),
                                "exp": datetime.now(timezone.utc) + expiry
                            }, 
                        algorithm = securuity_settings.JWT_ALGORITHM,
                        key = securuity_settings.JWT_SECRET
        )
    return token

def decode_access_token(token:str)->dict:

    try:
        data = jwt.decode(
            jwt=token, algorithms= [securuity_settings.JWT_ALGORITHM],
            key = securuity_settings.JWT_SECRET
        )
        return data
    except jwt.ExpiredSignatureError:
        raise InvalidToken()
    except jwt.PyJWTError: 
        return None 

    
app_directories = Path(__file__).resolve().parent
template_directory = app_directories.joinpath("template")

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
_selializer = URLSafeTimedSerializer(securuity_settings.JWT_SECRET)

def generate_email_token(data: dict,salt:str ,) -> str:
    return _selializer.dumps(data, salt=salt)

def decode_email_token(token: str, salt:str , expiry: timedelta|None = None  ) -> dict | None:
    try:
        data = _selializer.loads(
            token,
            salt=salt,
            max_age=expiry.total_seconds() if expiry else None
        )
        return data
    except (BadSignature , SignatureExpired): 
        #ไม่ถุกต้องหรือหมดอายุ
        return None