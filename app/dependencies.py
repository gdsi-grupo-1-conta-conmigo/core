from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel
import os
import jwt
from supabase import create_client, Client

# Replace with your Supabase Project URL and Anon Key
# It's recommended to use environment variables for these
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "YOUR_SUPABASE_KEY")

# JWT Configuration
JWT_ALGORITHM = "HS256"
JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("SUPABASE_JWT_SECRET environment variable is not set")

# Initialize the Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    # Handle cases where URL or Key might be missing or invalid at startup
    print(f"Error initializing Supabase client: {e}")
    print("Please ensure SUPABASE_URL and SUPABASE_KEY are set correctly.")
    supabase = None  # type: ignore

# Security scheme
security = HTTPBearer()

class UserClaims(BaseModel):
    iss: str
    sub: str
    aud: str
    exp: int
    iat: int
    email: str
    phone: Optional[str] = ""

def get_supabase_client() -> Client:
    """Dependency to get Supabase client instance"""
    return supabase

def auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserClaims:
    """Authentication dependency to get the current authenticated user"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            audience="authenticated"
        )
        user_claims = UserClaims(**payload)
        return user_claims
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token claims: {str(e)}")
