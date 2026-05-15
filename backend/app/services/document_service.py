import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.models import Document
from app.schemas import DocumentStatus
from app.services.file_service import validate_file, save_upload
from app.services.text_extractor import extract_text_from_file

logger = logging.getLogger("docuextract.documents")


async def process_upload(file: UploadFile, db: Session) -> tuple[Document, str | None]:
    """Upload, extract text, save to DB. Returns (document, duplicate_warning)."""
    try:
        validate_file(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        file_path, file_hash = await save_upload(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Duplicate check
    duplicate_warning = None
    existing = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing:
        duplicate_warning = "This document appears to have been uploaded before."
        logger.info("Duplicate detected: %s (matches doc %s)", file.filename, existing.id)

    # Extract text
    try:
        extracted_text = extract_text_from_file(file_path)
    except Exception as e:
        logger.error("Text extraction failed for %s: %s", file.filename, e)
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {e}")

    if not extracted_text or not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the document.")

    doc = Document(
        filename=file.filename,
        file_type=Path(file.filename).suffix.lower(),
        file_path=file_path,
        file_hash=file_hash,
        extracted_text=extracted_text,
        status=DocumentStatus.processed,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    logger.info("Document uploaded: %s (id=%s, chars=%d)", file.filename, doc.id, len(extracted_text))
    return doc, duplicate_warning
