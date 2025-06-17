from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
import jwt
from pydantic import BaseModel
from typing import Optional, List, Dict
from fastapi import Request

JWT_ALGORITHM = "HS256"
JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("SUPABASE_JWT_SECRET environment variable is not set")

class UserClaims(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int
    email: str
    phone: Optional[str] = ""

def verify_access_token(request):
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header is missing")

    # Split the authorization header into the scheme and the token
    scheme, token = authorization.split(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization scheme")

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            audience="authenticated"
        )
        user_claims = UserClaims(**payload)
        return user_claims
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token claims: {str(e)}")

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            user_claims = verify_access_token(request)
            request.state.user = user_claims
            response = await call_next(request)
            return response
        except HTTPException as exc:
            return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)
        except Exception as exc:
            return JSONResponse(content={"detail": f"Error: {str(exc)}"}, status_code=500)


def get_current_user(request: Request) -> Optional[UserClaims]:
    """Get the current authenticated user from request state"""
    if not hasattr(request.state, "user"):
        return None

    try:
        return UserClaims(**request.state.user)
    except Exception as e:
        return None
