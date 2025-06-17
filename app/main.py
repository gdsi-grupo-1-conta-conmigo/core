from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .routers import authentication, templates, template_data
from .dependencies import auth

# Create the FastAPI app instance
app = FastAPI(
    title="Conta Conmigo Core API",
    description="API for the Conta Conmigo platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include authentication router (no auth required)
app.include_router(
    authentication.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Include protected routers with authentication dependency
app.include_router(
    templates.router,
    prefix="/templates",
    tags=["Templates"],
    dependencies=[Depends(auth)]
)

app.include_router(
    template_data.router,
    prefix="/templates",
    tags=["Template Data"],
    dependencies=[Depends(auth)]
)

# Health check endpoint
@app.get("/health", response_class=JSONResponse, tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "API is running"}
