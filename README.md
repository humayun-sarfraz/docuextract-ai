# DocuExtract AI — Simple AI Document Data Extractor

AI-powered document data extraction tool. Upload PDFs, TXT, or DOCX files, define the fields you want to extract, and get clean structured JSON output with confidence scores.

## Features

- **Document Upload** — PDF, TXT, DOCX support with text extraction
- **Custom Field Schemas** — Define exactly what fields to extract
- **AI Extraction** — OpenAI-powered structured data extraction with confidence scores
- **Evidence Snippets** — See which document text the AI used for each field
- **Review Workflow** — Flag low-confidence and missing fields for manual review
- **Edit & Approve** — Manually correct extracted values before export
- **Export** — Download results as JSON or CSV
- **Duplicate Detection** — Warns when the same file is uploaded twice
- **Automation API** — One-shot endpoint for n8n, Zapier, Make integration

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| AI | OpenAI API |
| Validation | Pydantic |
| Database | SQLite |
| Frontend | Next.js, React, TypeScript |
| File Storage | Local uploads folder |
| Export | JSON, CSV |
| Containerization | Docker, Docker Compose |

## Project Structure

```
docuextract-ai/
  README.md
  .env.example
  docker-compose.yml
  backend/
    app/
      main.py              # FastAPI app entry point
      config.py             # Environment configuration
      database.py           # SQLite/SQLAlchemy setup
      models.py             # Database models
      schemas.py            # Pydantic schemas
      routes/
        documents.py        # Document upload & listing
        extraction.py       # Extraction & export endpoints
        automation.py       # Automation API
      services/
        text_extractor.py   # PDF/TXT/DOCX text extraction
        ai_extractor.py     # OpenAI extraction logic
        validation_service.py # Confidence & review logic
        export_service.py   # JSON/CSV export
        file_service.py     # File upload & validation
      storage/uploads/      # Uploaded files
    requirements.txt
    Dockerfile
  frontend/
    src/
      components/
        FileUpload.tsx
        SchemaBuilder.tsx
        ExtractionResults.tsx
        ReviewQueue.tsx
      app/
        page.tsx
        layout.tsx
        globals.css
      lib/
        api.ts
        types.ts
    package.json
    Dockerfile
  examples/
    sample-invoice.txt
    sample-fields.json
    sample-output.json
  docs/
    api-reference.md
    extraction-guide.md
```

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key

### Environment Variables

Copy the example env file and add your API key:

```bash
cp .env.example .env
```

Edit `.env`:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./docuextract.db
UPLOAD_DIR=./storage/uploads
MAX_UPLOAD_MB=10
CONFIDENCE_THRESHOLD=0.75
BACKEND_BASE_URL=http://localhost:8000
FRONTEND_BASE_URL=http://localhost:3000
```

### Run Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend runs at http://localhost:8000. API docs at http://localhost:8000/docs.

### Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000.

### Run with Docker Compose

```bash
# Create .env with your OPENAI_API_KEY first
docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

## Usage

### 1. Upload a Document

Go to http://localhost:3000 and upload a PDF, TXT, or DOCX file.

Or via API:

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@examples/sample-invoice.txt"
```

### 2. Define Fields

Use the Schema Builder to add fields you want to extract. For each field, specify:
- **Name** — Machine-friendly name (e.g., `vendor_name`)
- **Description** — What the AI should look for
- **Type** — `string`, `number`, `date`, or `boolean`
- **Required** — Whether to flag if missing

Or via API:

```bash
curl -X POST http://localhost:8000/api/extraction/extract \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "DOCUMENT_ID_HERE",
    "fields": [
      {
        "name": "vendor_name",
        "description": "Name of the invoice vendor",
        "type": "string",
        "required": true
      },
      {
        "name": "invoice_number",
        "description": "Invoice number",
        "type": "string",
        "required": true
      },
      {
        "name": "total_amount",
        "description": "Total invoice amount",
        "type": "number",
        "required": true
      }
    ]
  }'
```

### 3. Review Results

The extraction results show each field with:
- **Value** — Extracted data
- **Confidence** — Color-coded score (green/yellow/red)
- **Evidence** — Text snippet from the document

Low-confidence or missing required fields are flagged for review.

### 4. Edit and Approve

Click **Edit** on any field to manually correct the value. Click **Approve** when satisfied.

### 5. Export

- **Export JSON** — Download structured extraction as JSON
- **Export CSV** — Download as CSV with field_name, value, confidence, evidence columns

### Automation Endpoint

For integration with n8n, Zapier, Make, or custom scripts:

```bash
curl -X POST http://localhost:8000/api/automation/extract \
  -F "file=@invoice.pdf" \
  -F 'fields=[{"name":"vendor_name","description":"Vendor name","type":"string","required":true},{"name":"total_amount","description":"Total amount","type":"number","required":true}]'
```

Returns the complete extraction result in one call.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/documents/upload` | Upload document |
| GET | `/api/documents` | List documents |
| GET | `/api/documents/{id}` | Get document |
| POST | `/api/extraction/extract` | Extract fields from document |
| GET | `/api/extractions` | List extractions |
| GET | `/api/extractions/{id}` | Get extraction |
| PUT | `/api/extractions/{id}` | Update extraction |
| POST | `/api/extractions/{id}/approve` | Approve extraction |
| GET | `/api/extractions/{id}/export/json` | Export as JSON |
| GET | `/api/extractions/{id}/export/csv` | Export as CSV |
| POST | `/api/automation/extract` | One-shot automation endpoint |

See [docs/api-reference.md](docs/api-reference.md) for full details.

## Troubleshooting

| Issue | Solution |
|---|---|
| `OPENAI_API_KEY` not set | Add your key to `.env` file |
| Upload fails | Check file is PDF/TXT/DOCX and under 10MB |
| Empty extraction | Verify the document has readable text (not scanned image) |
| AI returns invalid JSON | Retry — the model occasionally produces malformed output |
| CORS errors | Ensure backend is running on port 8000 |
| Docker build fails | Ensure Docker and Docker Compose are installed |

## Future Improvements

- OCR support for scanned PDFs
- User authentication
- Role-based review workflow
- Batch document processing
- S3 or cloud storage
- Database export connectors
- Google Drive import
- Email inbox ingestion
- More advanced validation rules
- Document type detection
- Multi-page citation highlighting
