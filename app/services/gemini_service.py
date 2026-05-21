import google.generativeai as genai
from app.config import settings

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
