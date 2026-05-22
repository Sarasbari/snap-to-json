from fastapi import APIRouter, UploadFile, File, status
from fastapi.responses import JSONResponse
import time
import logging
from app.config import settings
from app.schemas.response import APIResponse
from app.schemas.invoice import InvoiceData
from app.services.gemini_service import extract_invoice_data, GeminiExtractionError
from app.services.parser_service import parse_invoice_response
from app.db.supabase_client import save_extraction

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/extract", response_model=APIResponse[InvoiceData])
async def extract_invoice(file: UploadFile = File(...)):
    """
    Endpoint to upload an invoice image and extract structured data using Gemini.
    """
    try:
        # 1. Validate file type — allow only image/jpeg, image/png, image/webp, image/tiff
        allowed_types = {"image/jpeg", "image/png", "image/webp", "image/tiff"}
        if file.content_type not in allowed_types:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=APIResponse(
                    success=False,
                    error=f"Invalid file type: '{file.content_type}'. Allowed types are: {', '.join(allowed_types)}"
                ).model_dump()
            )

        # 3. Read file bytes
        contents = await file.read()

        # 2. Validate file size — reject if > settings.MAX_FILE_SIZE_MB
        max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(contents) > max_size_bytes:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=APIResponse(
                    success=False,
                    error=f"File size exceeds maximum limit of {settings.MAX_FILE_SIZE_MB}MB."
                ).model_dump()
            )

        # 4. Record start time
        start_time = time.perf_counter()

        # 5. Call gemini_service.extract_invoice_data
        raw_text = await extract_invoice_data(contents, file.content_type)

        # 6. Call parser_service.parse_invoice_response
        invoice_data = parse_invoice_response(raw_text)

        # Save extraction to Supabase database
        try:
            await save_extraction(file.filename, invoice_data)
        except Exception as db_err:
            logger.error(f"Failed to save extraction to database for file '{file.filename}': {str(db_err)}")

        # 7. Calculate processing_time_ms
        end_time = time.perf_counter()
        processing_time_ms = (end_time - start_time) * 1000.0

        # 8. Return APIResponse[InvoiceData]
        return APIResponse(
            success=True,
            data=invoice_data,
            processing_time_ms=processing_time_ms
        )

    except Exception as e:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if isinstance(e, (GeminiExtractionError, ValueError)):
            status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

        return JSONResponse(
            status_code=status_code,
            content=APIResponse(
                success=False,
                error=str(e)
            ).model_dump()
        )


