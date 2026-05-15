import json
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Extraction
from app.schemas import AutomationResponse, FieldDefinition, FieldResult, ExtractionStatus
from app.services.document_service import process_upload
from app.services.ai_extractor import extract_fields
from app.services.validation_service import validate_extraction

logger = logging.getLogger("docuextract.automation")

router = APIRouter(prefix="/api/automation", tags=["automation"])


@router.post("/extract", response_model=AutomationResponse)
async def automation_extract(
    file: UploadFile = File(...),
    fields: str = Form(...),
    db: Session = Depends(get_db),
):
    # Upload & extract text (shared logic)
    doc, _ = await process_upload(file, db)

    # Parse fields
    try:
        fields_list = json.loads(fields)
        field_defs = [FieldDefinition(**f) for f in fields_list]
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid fields JSON: {e}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid field definitions: {e}")

    if not field_defs:
        raise HTTPException(status_code=400, detail="At least one field is required")

    # Extract with AI
    try:
        extracted_data = extract_fields(doc.extracted_text, field_defs)
    except Exception as e:
        logger.error("AI extraction failed for automation doc %s: %s", doc.id, e)
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {e}")

    missing, needs_review = validate_extraction(extracted_data, field_defs)

    # Save extraction
    extraction = Extraction(
        document_id=doc.id,
        fields_schema_json=json.dumps([f.model_dump() for f in field_defs]),
        extracted_json=json.dumps(extracted_data),
        missing_required_fields_json=json.dumps(missing),
        needs_review=needs_review,
        status=ExtractionStatus.pending_review,
    )
    db.add(extraction)
    db.commit()
    db.refresh(extraction)

    logger.info("Automation extraction complete: doc=%s, extraction=%s", doc.id, extraction.id)

    # Build response
    parsed_data = {}
    for k, v in extracted_data.items():
        if isinstance(v, dict):
            parsed_data[k] = FieldResult(**v)
        else:
            parsed_data[k] = FieldResult(value=v)

    return AutomationResponse(
        document_id=doc.id,
        extraction_id=extraction.id,
        extracted_data=parsed_data,
        missing_required_fields=missing,
        needs_review=needs_review,
    )
