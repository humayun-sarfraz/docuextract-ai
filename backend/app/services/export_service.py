import csv
import io
import json


def export_as_json(extraction_id: str, document_id: str, extracted_json: str) -> dict:
    data = json.loads(extracted_json)
    return {
        "document_id": document_id,
        "extraction_id": extraction_id,
        "extracted_data": data,
    }


def export_as_csv(extracted_json: str) -> str:
    data = json.loads(extracted_json)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["field_name", "value", "confidence", "evidence"])

    for field_name, field_data in data.items():
        if isinstance(field_data, dict):
            value = field_data.get("value")
            writer.writerow([
                field_name,
                "null" if value is None else value,
                field_data.get("confidence", ""),
                field_data.get("evidence", ""),
            ])

    return output.getvalue()
