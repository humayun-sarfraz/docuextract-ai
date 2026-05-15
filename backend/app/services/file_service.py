import hashlib
import re
import uuid
from pathlib import Path
from fastapi import UploadFile
from app.config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_MB


def validate_file(file: UploadFile) -> None:
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")


def sanitize_filename(filename: str) -> str:
    name = Path(filename).stem
    ext = Path(filename).suffix.lower()
    name = re.sub(r"[^\w\-.]", "_", name)
    return f"{name}_{uuid.uuid4().hex[:8]}{ext}"


async def save_upload(file: UploadFile) -> tuple[str, str]:
    """Save uploaded file. Returns (file_path, file_hash)."""
    content = await file.read()

    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise ValueError(f"File too large. Maximum size: {MAX_UPLOAD_MB}MB")

    file_hash = hashlib.sha256(content).hexdigest()
    safe_name = sanitize_filename(file.filename)
    file_path = Path(UPLOAD_DIR) / safe_name
    file_path.write_bytes(content)

    return str(file_path), file_hash
