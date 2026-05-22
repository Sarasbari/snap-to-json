import base64
import json
import google.generativeai as genai
from app.config import settings
from app.schemas.invoice import InvoiceData

class GeminiExtractionError(Exception):
    """Exception raised when Gemini API fails or returns invalid/unparsable response."""
    pass

async def extract_invoice_data(image_bytes: bytes, mime_type: str) -> dict:
    """
    Extracts structured invoice data from image bytes using Gemini 1.5 Flash.
    """
    try:
        # 1. Init Gemini client using settings.GEMINI_API_KEY
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # 2. Use model: "gemini-1.5-flash"
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # 3. Build a prompt
        schema = json.dumps(InvoiceData.model_json_schema(), indent=2)
        prompt = (
            "You are an invoice data extraction expert.\n"
            "Analyze the provided invoice image and extract the data into the following JSON schema:\n"
            f"{schema}\n\n"
            "Rules:\n"
            "1. Return ONLY valid JSON, with no markdown formatting (do not wrap in ```json or ```), no explanation, and no backticks.\n"
            "2. If a field is missing from the invoice, return null for it.\n"
        )
        
        # 4. Send image as inline_data with the mime_type
        image_data = base64.b64encode(image_bytes).decode("utf-8")
        image_part = {
            "inline_data": {
                "mime_type": mime_type,
                "data": image_data
            }
        }
        
        # Call generate_content_async
        response = await model.generate_content_async(
            contents=[prompt, image_part]
        )
        
        # 5. Return response.text (raw string) parsed as dict to match the -> dict signature.
        raw_text = response.text
        if not raw_text:
            raise GeminiExtractionError("Received empty response from Gemini API.")
            
        cleaned_text = raw_text.strip()
        # Strip potential markdown formatting if Gemini included it despite instructions
        if cleaned_text.startswith("```"):
            lines = cleaned_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()
            
        parsed_data = json.loads(cleaned_text)
        if not isinstance(parsed_data, dict):
            raise GeminiExtractionError("Parsed Gemini response is not a JSON object/dictionary.")
            
        return parsed_data
        
    except Exception as e:
        if isinstance(e, GeminiExtractionError):
            raise e
        raise GeminiExtractionError(f"Error during Gemini extraction: {str(e)}") from e

class GeminiService:
    def __init__(self):
        # Configure the Gemini API client
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Placeholder for model selection

    async def analyze_invoice_image(self, image_bytes: bytes, mime_type: str) -> str:
        """
        Sends invoice image bytes to Gemini Vision model and returns raw response text.
        """
        # Stub implementation
        return "Stub response from Gemini API"

