import os
from fastapi import Header
from supabase import create_client, Client
from fastapi import Depends, HTTPException
from typing import Dict, Any 

# Replace with your Supabase Project URL and Anon Key
# It's recommended to use environment variables for these
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "YOUR_SUPABASE_KEY")

# Initialize the Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    # Handle cases where URL or Key might be missing or invalid at startup
    print(f"Error initializing Supabase client: {e}")
    print("Please ensure SUPABASE_URL and SUPABASE_KEY are set correctly.")
    supabase = None  # type: ignore

async def get_supabase_client() -> Client:
    """Dependency to get Supabase client instance"""
    if supabase is None:
        raise RuntimeError("Supabase client is not initialized. Check your environment variables.")
    return supabase

async def get_current_user(
    Authorization: str = Header(...),
    supabase: Client = Depends(get_supabase_client),
) -> str:
    """
    Read the Bearer token, ask Supabase for the user,
    and return a plain dict of user fields.
    """
    try:
        scheme, _, token = Authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(status_code=401, detail="Invalid or missing auth token")

        res: Any = supabase.auth.get_user(token)
        user = res.user
        if user is None:
            raise HTTPException(401, "User not authenticated")

            # This picks up *all* public attributes
        return user.id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


