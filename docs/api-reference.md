# DocuExtract AI — API Reference

Base URL: `http://localhost:8000`

---

## Health Check

```
GET /health
```

Response:
```json
{"status": "ok", "service": "DocuExtract AI"}
```

---

## Documents

### Upload Document

```
POST /api/documents/upload
Content-Type: multipart/form-data
```

Form data:
- `file` — PDF, TXT, or DOCX file (max 10MB)

Response: `DocumentResponse` with `document_id`

### List Documents

```
GET /api/documents
```

### Get Document

```
GET /api/documents/{document_id}
```

---

## Extraction

### Extract Fields

```
POST /api/extraction/extract
Content-Type: application/json
```

Body:
```json
{
  "document_id": "string",
  "fields": [
    {
      "name": "field_name",
      "description": "What to extract",
      "type": "string|number|date|boolean",
      "required": true
    }
  ]
}
```

Response: `ExtractionResponse` with extracted data, confidence scores, and evidence.

### List Extractions

```
GET /api/extractions
```

### Get Extraction

```
GET /api/extractions/{extraction_id}
```

### Update Extraction

```
PUT /api/extractions/{extraction_id}
Content-Type: application/json
```

Body:
```json
{
  "extracted_data": {
    "field_name": {
      "value": "new value",
      "confidence": 1.0,
      "evidence": "Manually edited"
    }
  }
}
```

### Approve Extraction

```
POST /api/extractions/{extraction_id}/approve
```

---

## Export

### Export as JSON

```
GET /api/extractions/{extraction_id}/export/json
```

### Export as CSV

```
GET /api/extractions/{extraction_id}/export/csv
```

---

## Automation

### Extract from File (one-shot)

```
POST /api/automation/extract
Content-Type: multipart/form-data
```

Form data:
- `file` — Document file
- `fields` — JSON string of field definitions

Response: Extraction result with document_id and extraction_id.
