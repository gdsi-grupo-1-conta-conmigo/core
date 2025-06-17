import os
from dotenv import load_dotenv
import base64

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import time
import jwt
from jwt.exceptions import InvalidTokenError

from .routers import authentication, templates, template_data
from .auth_middleware import AuthMiddleware

# Create the FastAPI app instance
app = FastAPI(
    title="My FastAPI App",
    description="A FastAPI application with Supabase authentication.",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(
    authentication.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Create a sub-application for templates with middleware
authenticated_app = FastAPI()
authenticated_app.add_middleware(AuthMiddleware)
authenticated_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the templates router with middleware
authenticated_app.include_router(
    templates.router,
    prefix="/templates",
    tags=["Templates"]
)

# Mount the template data router with middleware
authenticated_app.include_router(
    template_data.router,
    prefix="/templates",  # We use the same prefix to nest under templates
    tags=["Template Data"]
)

app.mount("/api", authenticated_app)

# Health check endpoint
@app.get("/health", response_class=JSONResponse, tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "API is running"}
