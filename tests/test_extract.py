from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_extract_stub():
    # Stub test for checking endpoint accessibility and response format
    files = {"file": ("test.png", b"dummy image bytes", "image/png")}
    response = client.post("/api/v1/extract", files=files)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["invoice_number"] == "INV-STUB-123"
