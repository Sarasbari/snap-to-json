from fastapi import APIRouter, Query, HTTPException, status
from app.schemas.response import APIResponse
from app.db import supabase_client as db

router = APIRouter()

@router.get("/history", response_model=APIResponse[list])
async def get_history(limit: int = Query(default=20, ge=1, le=100)):
    """
    Endpoint to retrieve history of parsed invoices from Supabase.
    """
    try:
        extractions = await db.get_extractions(limit)
        return APIResponse(
            success=True,
            data=extractions,
            error=None
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve history: {str(e)}"
        )

@router.get("/history/{extraction_id}", response_model=APIResponse[dict])
async def get_extraction(extraction_id: str):
    """
    Endpoint to retrieve a single parsed invoice extraction by ID.
    """
    try:
        extraction = await db.get_extraction_by_id(extraction_id)
        if not extraction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Extraction with ID {extraction_id} not found"
            )
        return APIResponse(
            success=True,
            data=extraction,
            error=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve extraction: {str(e)}"
        )

