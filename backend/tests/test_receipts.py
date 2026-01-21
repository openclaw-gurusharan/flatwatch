# Tests for receipts endpoints
import pytest
import os
from fastapi.testclient import TestClient
from pathlib import Path

from app.main import app
from app.routers.receipts import UPLOAD_DIR
from app.database import init_db, get_db_path


@pytest.fixture(autouse=True)
def setup_upload_dir():
    """Ensure upload directory exists and database initialized."""
    init_db()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield
    # Clean up uploaded files
    for file in UPLOAD_DIR.iterdir():
        if file.is_file():
            file.unlink()
    # Clean up database
    db_path = get_db_path()
    if db_path.exists():
        os.remove(db_path)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """Get auth token."""
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@flatwatch.test", "password": "any"},
    )
    return response.json()["access_token"]


def test_upload_receipt(client, auth_token):
    """Test uploading a receipt file."""
    from io import BytesIO

    file_content = b"test receipt content"
    response = client.post(
        "/api/receipts/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("test_receipt.pdf", BytesIO(file_content), "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert data["original_filename"] == "test_receipt.pdf"


def test_upload_without_auth(client):
    """Test upload requires authentication."""
    from io import BytesIO

    response = client.post(
        "/api/receipts/upload",
        files={"file": ("test.pdf", BytesIO(b"content"), "application/pdf")},
    )
    assert response.status_code == 401


def test_list_receipts(client, auth_token):
    """Test listing receipts."""
    response = client.get(
        "/api/receipts/list",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "files" in data


def test_get_receipt(client, auth_token):
    """Test getting receipt info."""
    # First upload a file
    from io import BytesIO

    upload_response = client.post(
        "/api/receipts/upload",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("test.pdf", BytesIO(b"content"), "application/pdf")},
    )
    filename = upload_response.json()["filename"]

    # Get file info
    response = client.get(
        f"/api/receipts/{filename}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
