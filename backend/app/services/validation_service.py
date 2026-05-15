from app.schemas import FieldDefinition
from app.config import CONFIDENCE_THRESHOLD


def validate_extraction(
    extracted_data: dict, fields: list[FieldDefinition]
) -> tuple[list[str], bool]:
    """Returns (missing_required_fields, needs_review)."""
    missing = []
    needs_review = False

    for field in fields:
        field_data = extracted_data.get(field.name)

        if field_data is None or field_data.get("value") is None:
            if field.required:
                missing.append(field.name)
                needs_review = True
            continue

        confidence = field_data.get("confidence", 0)
        if confidence < CONFIDENCE_THRESHOLD:
            needs_review = True

    return missing, needs_review
