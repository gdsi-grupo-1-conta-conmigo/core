from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel
import os
from supabase import create_client, Client

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

def get_supabase_client() -> Client:
    """Dependency to get Supabase client instance"""
    return supabase
