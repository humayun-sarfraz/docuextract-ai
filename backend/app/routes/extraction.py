import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models import Document, Extraction
from app.schemas import (
    ExtractionRequest,
    ExtractionResponse,
    ExtractionListResponse,
    ExtractionUpdateRequest,
    ExtractionStatus,
    FieldResult,
)
from app.services.ai_extractor import extract_fields
from app.services.validation_service import validate_extraction
from app.services.export_service import export_as_json, export_as_csv

logger = logging.getLogger("docuextract.extraction")

router = APIRouter(tags=["extractions"])


def _build_extraction_response(extraction: Extraction) -> ExtractionResponse:
    extracted_data = json.loads(extraction.extracted_json) if extraction.extracted_json else {}
    missing = json.loads(extraction.missing_required_fields_json) if extraction.missing_required_fields_json else []

    parsed_data = {}
    for k, v in extracted_data.items():
        if isinstance(v, dict):
            parsed_data[k] = FieldResult(**v)
        else:
            parsed_data[k] = FieldResult(value=v)

    return ExtractionResponse(
        id=extraction.id,
        document_id=extraction.document_id,
        extracted_data=parsed_data,
        missing_required_fields=missing,
        needs_review=extraction.needs_review,
        status=extraction.status,
        created_at=extraction.created_at,
        updated_at=extraction.updated_at,
    )


@router.post("/api/extraction/extract", response_model=ExtractionResponse)
def extract_data(req: ExtractionRequest, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == req.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not doc.extracted_text:
        raise HTTPException(status_code=400, detail="Document has no extracted text")

    # Check for duplicate field names
    field_names = [f.name for f in req.fields]
    if len(field_names) != len(set(field_names)):
        raise HTTPException(status_code=400, detail="Duplicate field names are not allowed")

    try:
        extracted_data = extract_fields(doc.extracted_text, req.fields)
    except Exception as e:
        logger.error("AI extraction failed for doc %s: %s", doc.id, e)
        raise HTTPException(status_code=500, detail=f"AI extraction failed: {e}")

    missing, needs_review = validate_extraction(extracted_data, req.fields)

    extraction = Extraction(
        document_id=doc.id,
        fields_schema_json=json.dumps([f.model_dump() for f in req.fields]),
        extracted_json=json.dumps(extracted_data),
        missing_required_fields_json=json.dumps(missing),
        needs_review=needs_review,
        status=ExtractionStatus.pending_review,
    )
    db.add(extraction)
    db.commit()
    db.refresh(extraction)

    logger.info(
        "Extraction complete: id=%s, doc=%s, fields=%d, needs_review=%s",
        extraction.id, doc.id, len(extracted_data), needs_review,
    )
    return _build_extraction_response(extraction)


@router.get("/api/extractions", response_model=list[ExtractionListResponse])
def list_extractions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    needs_review: bool | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Extraction)
    if needs_review is not None:
        query = query.filter(Extraction.needs_review == needs_review)
    results = query.order_by(Extraction.created_at.desc()).offset(skip).limit(limit).all()
    return results


@router.get("/api/extractions/{extraction_id}", response_model=ExtractionResponse)
def get_extraction(extraction_id: str, db: Session = Depends(get_db)):
    extraction = db.query(Extraction).filter(Extraction.id == extraction_id).first()
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")
    return _build_extraction_response(extraction)


@router.put("/api/extractions/{extraction_id}", response_model=ExtractionResponse)
def update_extraction(
    extraction_id: str, req: ExtractionUpdateRequest, db: Session = Depends(get_db)
):
    extraction = db.query(Extraction).filter(Extraction.id == extraction_id).first()
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")

    updated_data = {k: v.model_dump() for k, v in req.extracted_data.items()}
    extraction.extracted_json = json.dumps(updated_data)
    extraction.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(extraction)

    logger.info("Extraction updated: %s", extraction_id)
    return _build_extraction_response(extraction)


@router.post("/api/extractions/{extraction_id}/approve", response_model=ExtractionResponse)
def approve_extraction(extraction_id: str, db: Session = Depends(get_db)):
    extraction = db.query(Extraction).filter(Extraction.id == extraction_id).first()
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")

    extraction.status = ExtractionStatus.approved
    extraction.needs_review = False
    extraction.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(extraction)

    logger.info("Extraction approved: %s", extraction_id)
    return _build_extraction_response(extraction)


@router.get("/api/extractions/{extraction_id}/export/json")
def export_json(extraction_id: str, db: Session = Depends(get_db)):
    extraction = db.query(Extraction).filter(Extraction.id == extraction_id).first()
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")

    data = export_as_json(extraction.extracted_json)
    return JSONResponse(content=data)


@router.get("/api/extractions/{extraction_id}/export/csv")
def export_csv(extraction_id: str, db: Session = Depends(get_db)):
    extraction = db.query(Extraction).filter(Extraction.id == extraction_id).first()
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")

    csv_content = export_as_csv(extraction.extracted_json)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=extraction_{extraction_id}.csv"},
    )
