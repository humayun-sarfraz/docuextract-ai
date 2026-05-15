import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./docuextract.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "storage" / "uploads"))
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("docuextract")


def validate_config():
    """Validate required configuration at startup."""
    if not OPENAI_API_KEY:
        logger.warning(
            "OPENAI_API_KEY is not set. Extraction endpoints will fail. "
            "Set it in your .env file."
        )
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    logger.info("Upload directory: %s", UPLOAD_DIR)
    logger.info("Database: %s", DATABASE_URL)
    logger.info("OpenAI model: %s", OPENAI_MODEL)
    logger.info("Confidence threshold: %s", CONFIDENCE_THRESHOLD)
