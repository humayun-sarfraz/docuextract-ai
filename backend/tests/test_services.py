import os
import tempfile
from pathlib import Path

from app.services.text_extractor import extract_text_from_file
from app.services.validation_service import validate_extraction
from app.services.export_service import export_as_json, export_as_csv
from app.services.file_service import sanitize_filename, validate_file
from app.schemas import FieldDefinition, FieldType

import pytest


class TestTextExtractor:
    def test_extract_txt(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Hello world\nLine two")
        result = extract_text_from_file(str(f))
        assert "Hello world" in result
        assert "Line two" in result

    def test_unsupported_format(self, tmp_path):
        f = tmp_path / "test.xyz"
        f.write_text("data")
        with pytest.raises(ValueError, match="Unsupported"):
            extract_text_from_file(str(f))


class TestValidation:
    def test_all_fields_present_high_confidence(self):
        extracted = {
            "name": {"value": "Acme", "confidence": 0.95, "evidence": "Acme"},
        }
        fields = [FieldDefinition(name="name", type=FieldType.string, required=True)]
        missing, needs_review = validate_extraction(extracted, fields)
        assert missing == []
        assert needs_review is False

    def test_missing_required_field(self):
        extracted = {
            "name": {"value": None, "confidence": 0, "evidence": None},
        }
        fields = [FieldDefinition(name="name", type=FieldType.string, required=True)]
        missing, needs_review = validate_extraction(extracted, fields)
        assert "name" in missing
        assert needs_review is True

    def test_low_confidence_triggers_review(self):
        extracted = {
            "name": {"value": "Acme", "confidence": 0.5, "evidence": "maybe Acme"},
        }
        fields = [FieldDefinition(name="name", type=FieldType.string, required=False)]
        missing, needs_review = validate_extraction(extracted, fields)
        assert missing == []
        assert needs_review is True

    def test_optional_missing_no_review(self):
        extracted = {
            "name": {"value": None, "confidence": 0, "evidence": None},
        }
        fields = [FieldDefinition(name="name", type=FieldType.string, required=False)]
        missing, needs_review = validate_extraction(extracted, fields)
        assert missing == []
        assert needs_review is False

    def test_field_not_in_result(self):
        extracted = {}
        fields = [FieldDefinition(name="name", type=FieldType.string, required=True)]
        missing, needs_review = validate_extraction(extracted, fields)
        assert "name" in missing
        assert needs_review is True


class TestExportService:
    def test_export_json(self):
        json_str = '{"vendor": {"value": "Acme", "confidence": 0.9, "evidence": "Vendor: Acme"}}'
        result = export_as_json(json_str)
        assert result["vendor"]["value"] == "Acme"

    def test_export_csv(self):
        json_str = '{"vendor": {"value": "Acme", "confidence": 0.9, "evidence": "Vendor: Acme"}}'
        csv = export_as_csv(json_str)
        assert "field_name" in csv
        assert "vendor" in csv
        assert "Acme" in csv
        assert "0.9" in csv


class TestFileService:
    def test_sanitize_filename(self):
        result = sanitize_filename("my invoice (2).pdf")
        assert result.endswith(".pdf")
        assert "(" not in result
        assert " " not in result

    def test_sanitize_preserves_extension(self):
        result = sanitize_filename("document.docx")
        assert result.endswith(".docx")
