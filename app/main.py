from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.extract import router as extract_router
from app.api.v1.history import router as history_router

app = FastAPI(
    title="Snap to JSON API",
    description="FastAPI backend to parse invoices into JSON using Gemini Vision API and Supabase.",
    version="1.0.0"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(extract_router, prefix="/api/v1", tags=["extract"])
app.include_router(history_router, prefix="/api/v1", tags=["history"])

@app.get("/")
async def root():
    return {"message": "Welcome to Snap to JSON API. The service is running."}
