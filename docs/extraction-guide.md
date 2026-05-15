# DocuExtract AI — Extraction Guide

## How It Works

1. **Upload** a document (PDF, TXT, or DOCX)
2. **Define fields** you want to extract (name, type, description, required)
3. **AI extracts** structured data from the document text
4. **Review** results — check confidence scores and evidence
5. **Export** as JSON or CSV

## Defining Fields

Each field needs:

| Property | Description | Example |
|---|---|---|
| `name` | Machine-friendly field name | `invoice_number` |
| `description` | Human description for the AI | `"Invoice number or reference"` |
| `type` | Data type | `string`, `number`, `date`, `boolean` |
| `required` | Flag missing values | `true` / `false` |

## Understanding Results

For each field, the AI returns:
- **value** — The extracted value, or `null` if not found
- **confidence** — Score from 0.0 to 1.0
- **evidence** — Short text snippet from the document

## Confidence Scores

- **85%+** (green) — High confidence, likely correct
- **75-84%** (yellow) — Medium confidence, verify
- **Below 75%** (red) — Low confidence, needs manual review

## Review Rules

An extraction is flagged for review when:
- Any **required** field is missing (value is null)
- Any field has confidence **below 0.75**

## Tips

- Write clear field descriptions — the AI uses them to understand what to look for
- Use the correct type — `number` for amounts, `date` for dates
- Mark critical fields as `required` so missing values are flagged
- Review evidence snippets to verify the AI found the right text

## Automation

Use the `/api/automation/extract` endpoint to integrate with n8n, Zapier, or custom scripts:

```bash
curl -X POST http://localhost:8000/api/automation/extract \
  -F "file=@invoice.pdf" \
  -F 'fields=[{"name":"total","description":"Total amount","type":"number","required":true}]'
```
