# Tests for transactions endpoints
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db, get_db_path, get_db_connection


@pytest.fixture(autouse=True)
def setup_database():
    """Initialize database before each test."""
    init_db()
    yield
    # Clean up after test
    import os
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


def test_list_transactions_empty(client, auth_token):
    """Test listing transactions when empty."""
    response = client.get(
        "/api/transactions",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_list_transactions_unauthorized(client):
    """Test listing transactions without auth."""
    response = client.get("/api/transactions")
    assert response.status_code == 401


def test_trigger_sync(client, auth_token):
    """Test triggering transaction sync."""
    response = client.post(
        "/api/transactions/sync",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "saved" in data
    assert data["saved"] >= 0


def test_get_summary(client, auth_token):
    """Test getting financial summary."""
    # First sync some transactions
    client.post(
        "/api/transactions/sync",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    response = client.get(
        "/api/transactions/summary",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "balance" in data
    assert "total_inflow" in data
    assert "total_outflow" in data


def test_create_transaction(client, auth_token):
    """Test creating a transaction."""
    response = client.post(
        "/api/transactions",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "amount": 100.0,
            "transaction_type": "inflow",
            "description": "Test transaction",
            "vpa": "test@upi",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100.0
    assert data["description"] == "Test transaction"


def test_filter_transactions_by_type(client, auth_token):
    """Test filtering transactions by type."""
    # Sync some transactions
    client.post(
        "/api/transactions/sync",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    # Filter by inflow
    response = client.get(
        "/api/transactions?txn_type=inflow",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    for txn in data:
        assert txn["transaction_type"] == "inflow"


def test_sync_saves_transactions(client, auth_token):
    """Test that sync saves new transactions."""
    from app.database import get_db_connection

    # Clear existing transactions
    conn = get_db_connection()
    conn.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()

    # Trigger sync
    response = client.post(
        "/api/transactions/sync",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["saved"] > 0

    # Verify transactions in DB
    conn = get_db_connection()
    cursor = conn.execute("SELECT COUNT(*) as count FROM transactions")
    count = cursor.fetchone()["count"]
    conn.close()
    assert count > 0
