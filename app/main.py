from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import router as v1_router

app = FastAPI(
    title="snap-to-json"
)

# CORS enabled for all origins (dev mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints under /api/v1 prefix
app.include_router(v1_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Snap to JSON API. The service is running."}

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "env": settings.APP_ENV
    }
