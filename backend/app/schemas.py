from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re


# --- Enums ---

class FieldType(str, Enum):
    string = "string"
    number = "number"
    date = "date"
    boolean = "boolean"


class DocumentStatus(str, Enum):
    uploaded = "uploaded"
    processed = "processed"
    failed = "failed"


class ExtractionStatus(str, Enum):
    pending_review = "pending_review"
    approved = "approved"
    exported = "exported"


# --- Field Schema ---

class FieldDefinition(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    type: FieldType = FieldType.string
    required: bool = False

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", v):
            raise ValueError(
                "Field name must start with a letter and contain only letters, numbers, and underscores"
            )
        return v


# --- Document ---

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_type: str
    file_hash: Optional[str] = None
    extracted_text: Optional[str] = None
    status: str
    created_at: datetime
    duplicate_warning: Optional[str] = None


class DocumentListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_type: str
    status: str
    created_at: datetime


# --- Extraction ---

class ExtractionRequest(BaseModel):
    document_id: str
    fields: list[FieldDefinition] = Field(..., min_length=1)


class FieldResult(BaseModel):
    value: Optional[str | int | float | bool] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: Optional[str] = None


class ExtractionResponse(BaseModel):
    id: str
    document_id: str
    extracted_data: dict[str, FieldResult] = {}
    missing_required_fields: list[str] = []
    needs_review: bool = False
    status: str = ExtractionStatus.pending_review
    created_at: datetime
    updated_at: datetime


class ExtractionListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    needs_review: bool
    status: str
    created_at: datetime


class ExtractionUpdateRequest(BaseModel):
    extracted_data: dict[str, FieldResult]


# --- Automation ---

class AutomationResponse(BaseModel):
    document_id: str
    extraction_id: str
    extracted_data: dict[str, FieldResult] = {}
    missing_required_fields: list[str] = []
    needs_review: bool = False


# --- Pagination ---

class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
