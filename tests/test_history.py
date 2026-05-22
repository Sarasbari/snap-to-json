from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

def test_get_history_success():
    mock_extractions = [
        {"id": "uuid-1", "filename": "invoice1.png", "vendor": "Vendor A"},
        {"id": "uuid-2", "filename": "invoice2.png", "vendor": "Vendor B"}
    ]
    with patch("app.api.v1.history.db.get_extractions", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_extractions
        
        response = client.get("/api/v1/history?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["error"] is None
        assert len(data["data"]) == 2
        assert data["data"][0]["vendor"] == "Vendor A"
        mock_get.assert_called_once_with(10)

def test_get_history_default_limit():
    with patch("app.api.v1.history.db.get_extractions", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = []
        
        response = client.get("/api/v1/history")
        
        assert response.status_code == 200
        mock_get.assert_called_once_with(20)

def test_get_history_validation_error():
    # Limit exceeds 100
    response = client.get("/api/v1/history?limit=101")
    assert response.status_code == 422

    # Limit less than 1
    response = client.get("/api/v1/history?limit=0")
    assert response.status_code == 422

def test_get_extraction_by_id_success():
    mock_extraction = {"id": "uuid-123", "filename": "invoice.png", "vendor": "Vendor C"}
    with patch("app.api.v1.history.db.get_extraction_by_id", new_callable=AsyncMock) as mock_get_by_id:
        mock_get_by_id.return_value = mock_extraction
        
        response = client.get("/api/v1/history/uuid-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == "uuid-123"
        assert data["data"]["vendor"] == "Vendor C"
        mock_get_by_id.assert_called_once_with("uuid-123")

def test_get_extraction_by_id_not_found():
    with patch("app.api.v1.history.db.get_extraction_by_id", new_callable=AsyncMock) as mock_get_by_id:
        mock_get_by_id.return_value = None
        
        response = client.get("/api/v1/history/non-existent-uuid")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
        mock_get_by_id.assert_called_once_with("non-existent-uuid")
