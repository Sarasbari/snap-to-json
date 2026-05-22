from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.config import settings

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "snap-to-json" in response.text

def test_extract_success():
    # Mock extract_invoice_data returning a valid raw JSON string
    mock_raw_json = '{"vendor": "Acme Corp", "invoice_number": "INV-12345", "total_amount": 1200.5}'
    with patch("app.api.v1.extract.extract_invoice_data", new_callable=AsyncMock) as mock_extract, \
         patch("app.api.v1.extract.save_extraction", new_callable=AsyncMock) as mock_save:
        mock_extract.return_value = mock_raw_json
        mock_save.return_value = {"id": "dummy-uuid"}
        
        files = {"file": ("test.png", b"dummy image bytes", "image/png")}
        response = client.post("/api/v1/extract", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["error"] is None
        assert data["data"]["vendor"] == "Acme Corp"
        assert data["data"]["invoice_number"] == "INV-12345"
        assert data["data"]["total_amount"] == 1200.5
        assert isinstance(data["processing_time_ms"], float)
        
        # Verify extract_invoice_data was called with correct args
        mock_extract.assert_called_once_with(b"dummy image bytes", "image/png")
        # Verify save_extraction was called
        mock_save.assert_called_once()


def test_extract_invalid_file_type():
    files = {"file": ("test.txt", b"plain text content", "text/plain")}
    response = client.post("/api/v1/extract", files=files)
    
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert "Invalid file type" in data["error"]

def test_extract_file_size_exceeded():
    # Set MAX_FILE_SIZE_MB to 0 so any file size exceeds it
    with patch.object(settings, "MAX_FILE_SIZE_MB", 0):
        files = {"file": ("test.png", b"some bytes", "image/png")}
        response = client.post("/api/v1/extract", files=files)
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "File size exceeds maximum limit" in data["error"]

