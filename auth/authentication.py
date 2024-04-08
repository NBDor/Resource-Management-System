from fastapi import HTTPException
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from socketio.exceptions import ConnectionRefusedError
from config.settings import app_settings
from enum import Enum
import jwt

security = HTTPBearer()


def decode_access_token(auth: HTTPAuthorizationCredentials = Security(security)):
    if app_settings.TESTING:
        return {"token_type": "access", "sub": "test_user", "role": "admin", "is_superuser": True}
    try:
        token = auth.credentials
        payload = jwt.decode(
            token, app_settings.VERIFYING_KEY, algorithms=["RS256", "HS256"]
        )
        if payload["token_type"] != "access":
            raise HTTPException(
                status_code=401, detail="Invalid token type - must be access token"
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


def decode_socket_token(token: HTTPAuthorizationCredentials = Security(security)):
    try:
        token = token['token']
        payload = jwt.decode(
            token, app_settings.VERIFYING_KEY, algorithms=["RS256", "HS256"]
        )
        if payload["token_type"] != "access":
            raise ConnectionRefusedError("Invalid token type - must be access token")
        return payload
    except jwt.ExpiredSignatureError:
        raise ConnectionRefusedError("Signature has expired")
    except jwt.InvalidTokenError as e:
        raise ConnectionRefusedError(f"Invalid token: {e}")
