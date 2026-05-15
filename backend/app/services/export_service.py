import csv
import io
import json


def export_as_json(extracted_json: str) -> dict:
    return json.loads(extracted_json)


def export_as_csv(extracted_json: str) -> str:
    data = json.loads(extracted_json)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["field_name", "value", "confidence", "evidence"])

    for field_name, field_data in data.items():
        if isinstance(field_data, dict):
            writer.writerow([
                field_name,
                field_data.get("value", ""),
                field_data.get("confidence", ""),
                field_data.get("evidence", ""),
            ])

    return output.getvalue()
