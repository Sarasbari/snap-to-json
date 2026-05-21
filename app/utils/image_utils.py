from app.config import settings

def validate_image_file(file_content: bytes, filename: str) -> bool:
    """
    Validates that the file type is a supported image format and the file size 
    does not exceed MAX_FILE_SIZE_MB.
    """
    # Stub implementation - validation logic will go here
    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(file_content) > max_size_bytes:
        return False
    
    # Check allowed extensions
    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    ext = filename.lower()[filename.rfind("."):]
    return ext in allowed_extensions
