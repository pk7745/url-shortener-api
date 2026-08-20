import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import URL

# Load environment variables from .env
load_dotenv()

# Obtain DATABASE_URL exclusively from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is required for tests. "
        "Please configure DATABASE_URL in your environment or .env file."
    )

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Dependency override to yield test database sessions."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True, scope="module")
def setup_test_database():
    """Ensure tables exist in the test PostgreSQL database before running tests."""
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup tables after test module completes
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Provide TestClient instance."""
    with TestClient(app) as test_client:
        yield test_client


def test_shorten_url_success(client):
    """Test POST /shorten creates a shortened URL and returns valid response structure."""
    payload = {"url": "https://example.com/long/path/to/resource"}
    response = client.post("/shorten", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert "short_url" in data
    assert len(data["short_code"]) == 6
    assert data["short_url"].endswith(f"/{data['short_code']}")


def test_shorten_url_persisted_in_db(client):
    """Test that shortened URL record is actually persisted in PostgreSQL database."""
    target_url = "https://python.org/doc/fastapi"
    response = client.post("/shorten", json={"url": target_url})
    assert response.status_code == 201
    short_code = response.json()["short_code"]

    db = TestingSessionLocal()
    try:
        db_record = db.query(URL).filter(URL.short_code == short_code).first()
        assert db_record is not None
        assert db_record.original_url == target_url
        assert db_record.short_code == short_code
    finally:
        db.close()


def test_redirect_to_original_url(client):
    """Test GET /{short_code} issues a HTTP 307 redirect to the original URL."""
    target_url = "https://fastapi.tiangolo.com/tutorial/"
    response_post = client.post("/shorten", json={"url": target_url})
    short_code = response_post.json()["short_code"]

    response_get = client.get(f"/{short_code}", follow_redirects=False)
    assert response_get.status_code == 307
    assert response_get.headers["location"] == target_url


def test_redirect_unknown_short_code(client):
    """Test GET /{short_code} with non-existent short code returns HTTP 404."""
    response = client.get("/nonExistentCode99", follow_redirects=False)
    assert response.status_code == 404
    assert response.json()["detail"] == "Short URL not found"


def test_invalid_url_rejection(client):
    """Test POST /shorten with invalid URL is rejected with HTTP 422 validation error."""
    invalid_payloads = [
        {"url": "not-a-valid-url"},
        {"url": "ftp://unsupported-scheme.com"},
        {"url": ""},
    ]
    for payload in invalid_payloads:
        response = client.post("/shorten", json=payload)
        assert response.status_code == 422
