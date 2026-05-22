import pytest
from unittest.mock import MagicMock, patch
from app.schemas.invoice import InvoiceData, LineItem
from app.db.supabase_client import save_extraction, get_extractions, get_extraction_by_id

@pytest.mark.asyncio
async def test_save_extraction():
    # 1. Prepare sample InvoiceData
    invoice = InvoiceData(
        vendor="Mock Vendor",
        invoice_number="INV-123",
        invoice_date="2026-05-22",
        due_date="2026-06-22",
        total_amount=118.0,
        subtotal=100.0,
        tax_amount=18.0,
        currency="INR",
        line_items=[
            LineItem(description="Item 1", quantity=1.0, unit_price=100.0, total=100.0)
        ],
        payment_terms="Net 30",
        notes="Notes",
        confidence_score=0.9
    )
    
    # 2. Mock client response
    mock_client = MagicMock()
    mock_execute = MagicMock()
    mock_execute.return_value.data = [{"id": "some-uuid", "filename": "test.png", "vendor": "Mock Vendor"}]
    
    mock_client.table.return_value.insert.return_value.execute = mock_execute
    
    # 3. Patch get_supabase_client
    with patch("app.db.supabase_client.get_supabase_client", return_value=mock_client):
        result = await save_extraction("test.png", invoice)
        
        # Verify result
        assert result == {"id": "some-uuid", "filename": "test.png", "vendor": "Mock Vendor"}
        
        # Verify table name
        mock_client.table.assert_called_once_with("extractions")
        
        # Verify insert arguments
        mock_client.table.return_value.insert.assert_called_once()
        insert_data = mock_client.table.return_value.insert.call_args[0][0]
        
        assert insert_data["filename"] == "test.png"
        assert insert_data["vendor"] == "Mock Vendor"
        assert insert_data["invoice_number"] == "INV-123"
        assert insert_data["total_amount"] == 118.0
        assert insert_data["line_items"] == [
            {"description": "Item 1", "quantity": 1.0, "unit_price": 100.0, "total": 100.0}
        ]
        assert insert_data["raw_json"]["vendor"] == "Mock Vendor"

@pytest.mark.asyncio
async def test_get_extractions():
    # 1. Mock client response
    mock_client = MagicMock()
    mock_execute = MagicMock()
    mock_execute.return_value.data = [
        {"id": "uuid-1", "filename": "test1.png"},
        {"id": "uuid-2", "filename": "test2.png"}
    ]
    
    mock_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute = mock_execute
    
    # 2. Patch get_supabase_client
    with patch("app.db.supabase_client.get_supabase_client", return_value=mock_client):
        result = await get_extractions(limit=10)
        
        # Verify result
        assert result == [
            {"id": "uuid-1", "filename": "test1.png"},
            {"id": "uuid-2", "filename": "test2.png"}
        ]
        
        # Verify table name and query flow
        mock_client.table.assert_called_once_with("extractions")
        mock_client.table.return_value.select.assert_called_once_with("*")
        mock_client.table.return_value.select.return_value.order.assert_called_once_with("created_at", desc=True)
        mock_client.table.return_value.select.return_value.order.return_value.limit.assert_called_once_with(10)

@pytest.mark.asyncio
async def test_get_extraction_by_id_found():
    # 1. Mock client response
    mock_client = MagicMock()
    mock_execute = MagicMock()
    mock_execute.return_value.data = [{"id": "uuid-123", "filename": "test.png"}]
    
    mock_client.table.return_value.select.return_value.eq.return_value.execute = mock_execute
    
    # 2. Patch get_supabase_client
    with patch("app.db.supabase_client.get_supabase_client", return_value=mock_client):
        result = await get_extraction_by_id("uuid-123")
        
        # Verify result
        assert result == {"id": "uuid-123", "filename": "test.png"}
        
        # Verify query flow
        mock_client.table.assert_called_once_with("extractions")
        mock_client.table.return_value.select.assert_called_once_with("*")
        mock_client.table.return_value.select.return_value.eq.assert_called_once_with("id", "uuid-123")

@pytest.mark.asyncio
async def test_get_extraction_by_id_not_found():
    # 1. Mock client response
    mock_client = MagicMock()
    mock_execute = MagicMock()
    mock_execute.return_value.data = []
    
    mock_client.table.return_value.select.return_value.eq.return_value.execute = mock_execute
    
    # 2. Patch get_supabase_client
    with patch("app.db.supabase_client.get_supabase_client", return_value=mock_client):
        result = await get_extraction_by_id("uuid-123")
        
        # Verify result is None
        assert result is None
