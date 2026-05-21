# Snap to JSON - AI Invoice Extractor

Snap to JSON is a modern web application that automatically parses invoice images and extracts structured data (invoice number, vendor name, line items, tax, and totals) using the Gemini Vision API, saving the resulting metadata to Supabase.

## Tech Stack
*   **Backend:** Python FastAPI, Pydantic (data validation), `pydantic-settings` (config)
*   **Frontend:** HTML5, Tailwind CSS (via CDN), Vanilla JavaScript
*   **Database:** Supabase
*   **AI Engine:** Gemini Vision API (Google Generative AI SDK)
*   **Testing:** Pytest

## Project Structure
```
snap-to-json/
  app/
    __init__.py
    main.py              # FastAPI app, CORS, router registration
    config.py            # pydantic-settings, loads .env
    api/v1/__init__.py
    api/v1/extract.py    # POST /api/v1/extract (stub)
    api/v1/history.py    # GET /api/v1/history (stub)
    services/__init__.py
    services/gemini_service.py   # stub
    services/parser_service.py   # stub
    schemas/__init__.py
    schemas/invoice.py   # InvoiceData, LineItem Pydantic models
    schemas/response.py  # APIResponse wrapper
    db/__init__.py
    db/supabase_client.py        # init supabase client from env
    utils/__init__.py
    utils/image_utils.py         # validate file type, size
  frontend/
    index.html
    style.css
    app.js
  tests/
    __init__.py
    test_extract.py
    sample_invoices/     # empty placeholder
  .env.example
  .gitignore
  requirements.txt
  README.md
```

## Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd snap-to-json
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Environment Variables:**
    Copy `.env.example` to `.env` and fill in the values:
    ```bash
    cp .env.example .env
    ```

5.  **Run the Backend Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The API docs will be available at `http://127.0.0.1:8000/docs`.

6.  **Run the Frontend:**
    You can serve the `frontend/` folder using any local HTTP server, or simply open `frontend/index.html` in your browser.
