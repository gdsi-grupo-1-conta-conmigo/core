from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
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

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    access_token: str
    new_password: str

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
    
@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    supabase: Client = Depends(get_supabase_client),
):
    """
    Envía un correo con un enlace para restablecer la contraseña.
    """
    try:
        response = supabase.auth.reset_password_email(request.email)

        if "error" in response and response["error"]:
            raise HTTPException(status_code=400, detail=response["error"]["message"])

        return {"message": "Se envió un correo con instrucciones para restablecer tu contraseña."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    supabase: Client = Depends(get_supabase_client),
):
    """
    Cambia la contraseña usando el access_token enviado por Supabase en el correo.
    """
    try:
        # 1. Establecer la sesión con el access_token
        supabase.auth.set_session(request.access_token, None)

        # 2. Cambiar la contraseña del usuario autenticado
        response = supabase.auth.update_user({"password": request.new_password})

        if hasattr(response, "error") and response.error:
            raise HTTPException(status_code=400, detail=response.error.message)

        return {"message": "Contraseña actualizada correctamente."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))