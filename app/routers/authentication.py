from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from supabase import Client

from ..dependencies import get_supabase_client

router = APIRouter()

class UserCredentials(BaseModel):
    email: str
    password: str

class SignUpResponse(BaseModel):
    message: str
    user_id: str | None = None

class LogInResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str | None = None

@router.post("/signup", response_model=SignUpResponse)
async def signup(credentials: UserCredentials, supabase: Client = Depends(get_supabase_client)):
    """Create a new user account"""
    try:
        user_response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password,
        })
        if user_response.user:
            return {
                "message": "Signup successful. Please check your email for verification if enabled.",
                "user_id": user_response.user.id
            }
        elif user_response.error:
            raise HTTPException(status_code=400, detail=user_response.error.message)
        else:
            raise HTTPException(status_code=500, detail="Unknown error during sign up")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=LogInResponse)
async def login(credentials: UserCredentials, supabase: Client = Depends(get_supabase_client)):
    """Authenticate user and return access token"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        if response.session and response.session.access_token:
            return {
                "message": "Login successful",
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token
            }
        elif response.error:
            raise HTTPException(status_code=401, detail=response.error.message or "Invalid login credentials")
        else:
            raise HTTPException(status_code=500, detail="Unknown error during login or no session returned")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))