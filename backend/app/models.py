import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=True)
    extracted_text = Column(Text, nullable=True)
    status = Column(String, default="uploaded")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    fields_schema_json = Column(Text, nullable=True)
    extracted_json = Column(Text, nullable=True)
    missing_required_fields_json = Column(Text, nullable=True)
    needs_review = Column(Boolean, default=False)
    status = Column(String, default="pending_review")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
