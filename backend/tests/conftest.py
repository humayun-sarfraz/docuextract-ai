import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Set test env vars before importing app modules
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app
from app.database import Base, get_db


@pytest.fixture(scope="function")
def db_session(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_txt_file(tmp_path):
    file_path = tmp_path / "invoice.txt"
    file_path.write_text(
        "Invoice\n\n"
        "Vendor: Acme Office Supplies\n"
        "Invoice Number: INV-2025-1001\n"
        "Invoice Date: January 12, 2025\n"
        "Total Due: $1,101.60\n"
    )
    return file_path
