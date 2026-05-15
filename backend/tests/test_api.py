import io
import json
from unittest.mock import patch

import pytest


class TestHealthEndpoint:
    def test_health(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"


class TestDocumentUpload:
    def test_upload_txt(self, client):
        content = b"Invoice\nVendor: Acme\nTotal: $100"
        res = client.post(
            "/api/documents/upload",
            files={"file": ("invoice.txt", io.BytesIO(content), "text/plain")},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["filename"] == "invoice.txt"
        assert data["status"] == "processed"
        assert data["id"]
        assert "Acme" in data["extracted_text"]

    def test_upload_unsupported_type(self, client):
        res = client.post(
            "/api/documents/upload",
            files={"file": ("data.csv", io.BytesIO(b"a,b,c"), "text/csv")},
        )
        assert res.status_code == 400
        assert "Unsupported" in res.json()["detail"]

    def test_upload_empty_file(self, client):
        res = client.post(
            "/api/documents/upload",
            files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")},
        )
        assert res.status_code == 400

    def test_duplicate_warning(self, client):
        content = b"Same content here"
        client.post(
            "/api/documents/upload",
            files={"file": ("doc1.txt", io.BytesIO(content), "text/plain")},
        )
        res = client.post(
            "/api/documents/upload",
            files={"file": ("doc2.txt", io.BytesIO(content), "text/plain")},
        )
        assert res.status_code == 200
        assert res.json()["duplicate_warning"] is not None


class TestDocumentList:
    def test_list_empty(self, client):
        res = client.get("/api/documents")
        assert res.status_code == 200
        assert res.json() == []

    def test_list_after_upload(self, client):
        client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", io.BytesIO(b"content"), "text/plain")},
        )
        res = client.get("/api/documents")
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_pagination(self, client):
        for i in range(3):
            client.post(
                "/api/documents/upload",
                files={"file": (f"doc{i}.txt", io.BytesIO(f"content {i}".encode()), "text/plain")},
            )
        res = client.get("/api/documents?skip=0&limit=2")
        assert len(res.json()) == 2
        res = client.get("/api/documents?skip=2&limit=2")
        assert len(res.json()) == 1


class TestExtraction:
    @patch("app.routes.extraction.extract_fields")
    def test_extract_success(self, mock_extract, client):
        mock_extract.return_value = {
            "vendor_name": {"value": "Acme", "confidence": 0.95, "evidence": "Vendor: Acme"},
            "total": {"value": 100, "confidence": 0.9, "evidence": "Total: $100"},
        }

        # Upload first
        upload = client.post(
            "/api/documents/upload",
            files={"file": ("invoice.txt", io.BytesIO(b"Vendor: Acme\nTotal: $100"), "text/plain")},
        )
        doc_id = upload.json()["id"]

        # Extract
        res = client.post(
            "/api/extraction/extract",
            json={
                "document_id": doc_id,
                "fields": [
                    {"name": "vendor_name", "description": "Vendor", "type": "string", "required": True},
                    {"name": "total", "description": "Total", "type": "number", "required": True},
                ],
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["extracted_data"]["vendor_name"]["value"] == "Acme"
        assert data["needs_review"] is False

    def test_extract_document_not_found(self, client):
        res = client.post(
            "/api/extraction/extract",
            json={
                "document_id": "nonexistent",
                "fields": [{"name": "x", "description": "x", "type": "string", "required": False}],
            },
        )
        assert res.status_code == 404

    def test_extract_duplicate_fields_rejected(self, client):
        upload = client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", io.BytesIO(b"content"), "text/plain")},
        )
        doc_id = upload.json()["id"]

        res = client.post(
            "/api/extraction/extract",
            json={
                "document_id": doc_id,
                "fields": [
                    {"name": "vendor", "description": "x", "type": "string", "required": False},
                    {"name": "vendor", "description": "y", "type": "string", "required": False},
                ],
            },
        )
        assert res.status_code == 400
        assert "Duplicate" in res.json()["detail"]


class TestExtractionReview:
    @patch("app.routes.extraction.extract_fields")
    def test_approve(self, mock_extract, client):
        mock_extract.return_value = {
            "name": {"value": "Test", "confidence": 0.5, "evidence": "Test"},
        }

        upload = client.post(
            "/api/documents/upload",
            files={"file": ("doc.txt", io.BytesIO(b"Test content"), "text/plain")},
        )
        doc_id = upload.json()["id"]

        extract_res = client.post(
            "/api/extraction/extract",
            json={
                "document_id": doc_id,
                "fields": [{"name": "name", "description": "Name", "type": "string", "required": True}],
            },
        )
        ext_id = extract_res.json()["id"]
        assert extract_res.json()["needs_review"] is True

        # Approve
        approve_res = client.post(f"/api/extractions/{ext_id}/approve")
        assert approve_res.status_code == 200
        assert approve_res.json()["status"] == "approved"
        assert approve_res.json()["needs_review"] is False

    @patch("app.routes.extraction.extract_fields")
    def test_update_extraction(self, mock_extract, client):
        mock_extract.return_value = {
            "name": {"value": "Wrong", "confidence": 0.6, "evidence": "Wrong"},
        }

        upload = client.post(
            "/api/documents/upload",
            files={"file": ("doc.txt", io.BytesIO(b"Right content"), "text/plain")},
        )
        doc_id = upload.json()["id"]

        extract_res = client.post(
            "/api/extraction/extract",
            json={
                "document_id": doc_id,
                "fields": [{"name": "name", "description": "Name", "type": "string", "required": False}],
            },
        )
        ext_id = extract_res.json()["id"]

        # Update
        update_res = client.put(
            f"/api/extractions/{ext_id}",
            json={
                "extracted_data": {
                    "name": {"value": "Correct", "confidence": 1.0, "evidence": "Manually edited"},
                },
            },
        )
        assert update_res.status_code == 200
        assert update_res.json()["extracted_data"]["name"]["value"] == "Correct"


class TestExport:
    @patch("app.routes.extraction.extract_fields")
    def test_export_json(self, mock_extract, client):
        mock_extract.return_value = {
            "name": {"value": "Acme", "confidence": 0.95, "evidence": "Acme"},
        }

        upload = client.post(
            "/api/documents/upload",
            files={"file": ("doc.txt", io.BytesIO(b"Acme content"), "text/plain")},
        )
        extract_res = client.post(
            "/api/extraction/extract",
            json={
                "document_id": upload.json()["id"],
                "fields": [{"name": "name", "description": "Name", "type": "string", "required": False}],
            },
        )
        ext_id = extract_res.json()["id"]

        res = client.get(f"/api/extractions/{ext_id}/export/json")
        assert res.status_code == 200
        assert res.json()["name"]["value"] == "Acme"

    @patch("app.routes.extraction.extract_fields")
    def test_export_csv(self, mock_extract, client):
        mock_extract.return_value = {
            "name": {"value": "Acme", "confidence": 0.95, "evidence": "Acme"},
        }

        upload = client.post(
            "/api/documents/upload",
            files={"file": ("doc.txt", io.BytesIO(b"Acme content"), "text/plain")},
        )
        extract_res = client.post(
            "/api/extraction/extract",
            json={
                "document_id": upload.json()["id"],
                "fields": [{"name": "name", "description": "Name", "type": "string", "required": False}],
            },
        )
        ext_id = extract_res.json()["id"]

        res = client.get(f"/api/extractions/{ext_id}/export/csv")
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        assert "name" in res.text
        assert "Acme" in res.text
