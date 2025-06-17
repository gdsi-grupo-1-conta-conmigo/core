from fastapi import APIRouter, HTTPException, Depends, status
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
    user: dict

class LogOutResponse(BaseModel):
    message: str

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
        else:
            raise HTTPException(status_code=400, detail="Failed to create user account")

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

        if response.session and response.session.access_token and response.user:
            return {
                "message": "Login successful",
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": {
                    "id": response.user.id,
                    "email": response.user.email,
                    "user_metadata": response.user.user_metadata
                }
            }
        else:
            raise HTTPException(status_code=401, detail="Invalid login credentials")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout", response_model=LogOutResponse)
async def logout(supabase: Client = Depends(get_supabase_client)):
    """Log out the current user"""
    try:
        response = supabase.auth.sign_out()
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def get_current_user_info(supabase: Client = Depends(get_supabase_client)):
    """Get current authenticated user information"""
    try:
        # This endpoint will be protected by the middleware and dependency injection
        return {
            "message": "User authentication endpoint",
            "note": "Use this with Authorization: Bearer <token> header"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))