import logging
from app.schemas import FieldDefinition
from app.config import CONFIDENCE_THRESHOLD

logger = logging.getLogger("docuextract.validation")


def validate_extraction(
    extracted_data: dict, fields: list[FieldDefinition]
) -> tuple[list[str], bool]:
    """Returns (missing_required_fields, needs_review)."""
    missing = []
    needs_review = False

    for field in fields:
        field_data = extracted_data.get(field.name)

        # Handle missing field or malformed AI response (not a dict)
        if field_data is None or not isinstance(field_data, dict):
            if field_data is not None and not isinstance(field_data, dict):
                logger.warning(
                    "Field '%s' has malformed structure (expected dict, got %s), treating as missing",
                    field.name, type(field_data).__name__,
                )
            if field.required:
                missing.append(field.name)
                needs_review = True
            continue

        if field_data.get("value") is None:
            if field.required:
                missing.append(field.name)
                needs_review = True
            continue

        confidence = field_data.get("confidence", 0)
        if confidence < CONFIDENCE_THRESHOLD:
            needs_review = True

    return missing, needs_review
