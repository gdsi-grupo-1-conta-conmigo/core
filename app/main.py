from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create the FastAPI app instance
app = FastAPI(
    title="My FastAPI App",
    description="A base FastAPI application.",
    version="0.1.0"
)

# Root endpoint
@app.get("/", response_class=JSONResponse)
async def read_root():
    return {"message": "Welcome to your FastAPI app!"}

# Health check endpoint
@app.get("/health", response_class=JSONResponse, tags=["Health"])
async def health_check():
    return {"status": "ok"}

# You can add more routers or include APIRouters here
# from .routers import users
# app.include_router(users.router)
