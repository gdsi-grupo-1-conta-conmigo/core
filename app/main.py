from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .routers import authentication

# Create the FastAPI app instance
app = FastAPI(
    title="My FastAPI App",
    description="A base FastAPI application with authentication.",
    version="0.1.0"
)

# Include routers
app.include_router(
    authentication.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Root endpoint
@app.get("/", response_class=JSONResponse)
async def read_root():
    return {"message": "Welcome to your FastAPI app!"}

# Health check endpoint
@app.get("/health", response_class=JSONResponse, tags=["Health"])
async def health_check():
    return {"status": "ok"}

# You can add more routers here
# from .routers import users, items
# app.include_router(users.router)
# app.include_router(items.router)
