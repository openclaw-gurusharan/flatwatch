# Tests for audit logging
import pytest

from app.audit import AuditAction, log_action, get_audit_logs, get_audit_stats


@pytest.fixture(autouse=True)
def setup_database():
    """Initialize database before each test."""
    from app.database import init_db
    init_db()
    yield
    import os
    from app.database import get_db_path
    db_path = get_db_path()
    if db_path.exists():
        os.remove(db_path)


def test_log_action():
    """Test logging an action."""
    log_id = log_action(
        AuditAction.LOGIN,
        user_id=1,
        details="Test login",
        ip_address="127.0.0.1",
    )

    assert log_id > 0
    assert isinstance(log_id, int)


def test_get_audit_logs():
    """Test retrieving audit logs."""
    # Log some actions
    log_action(AuditAction.LOGIN, 1, "User 1 login", "127.0.0.1")
    log_action(AuditAction.TRANSACTION_CREATE, 1, "Created transaction", "127.0.0.1", 1, "transaction")
    log_action(AuditAction.CHALLENGE_CREATE, 2, "Created challenge", "127.0.0.1", 5, "challenge")

    # Get all logs
    logs = get_audit_logs()
    assert len(logs) >= 3

    # Most recent first
    assert logs[0]["action"] == AuditAction.CHALLENGE_CREATE.value


def test_get_audit_logs_by_user():
    """Test filtering audit logs by user."""
    log_action(AuditAction.LOGIN, 1, "User 1 login")
    log_action(AuditAction.LOGIN, 2, "User 2 login")
    log_action(AuditAction.TRANSACTION_CREATE, 1, "User 1 transaction")

    # Get logs for user 1 only
    logs = get_audit_logs(user_id=1)
    assert all(log["user_id"] == 1 for log in logs)
    assert len(logs) == 2


def test_get_audit_logs_by_action():
    """Test filtering audit logs by action type."""
    log_action(AuditAction.LOGIN, 1, "Login 1")
    log_action(AuditAction.TRANSACTION_CREATE, 1, "Tx 1")
    log_action(AuditAction.LOGIN, 2, "Login 2")

    # Get only login logs
    logs = get_audit_logs(action=AuditAction.LOGIN)
    assert all(log["action"] == AuditAction.LOGIN.value for log in logs)
    assert len(logs) == 2


def test_get_audit_logs_by_target():
    """Test filtering audit logs by target."""
    log_action(AuditAction.TRANSACTION_VERIFY, 1, "Verified tx 1", target_id=1, target_type="transaction")
    log_action(AuditAction.TRANSACTION_VERIFY, 1, "Verified tx 2", target_id=2, target_type="transaction")
    log_action(AuditAction.CHALLENGE_CREATE, 2, "Challenge", target_id=1, target_type="transaction")

    # Get logs for transaction 1
    logs = get_audit_logs(target_id=1)
    assert all(log["target_id"] == 1 for log in logs)
    assert len(logs) == 2


def test_get_audit_stats():
    """Test audit statistics."""
    # Log some actions
    log_action(AuditAction.LOGIN, 1, "Login 1")
    log_action(AuditAction.LOGIN, 2, "Login 2")
    log_action(AuditAction.TRANSACTION_CREATE, 1, "Tx 1")

    stats = get_audit_stats()

    assert stats["total"] >= 3
    assert "by_action" in stats
    assert "by_user" in stats
    assert stats["by_action"].get(AuditAction.LOGIN.value, 0) >= 2


def test_audit_log_immutability():
    """Test that audit logs have all required fields."""
    log_id = log_action(
        AuditAction.SIGNUP,
        user_id=5,
        details="New user signup",
        ip_address="192.168.1.1",
        target_id=5,
        target_type="user",
    )

    logs = get_audit_logs()
    log = next((l for l in logs if l["id"] == log_id), None)

    assert log is not None
    assert log["action"] == AuditAction.SIGNUP.value
    assert log["user_id"] == 5
    assert log["details"] == "New user signup"
    assert log["ip_address"] == "192.168.1.1"
    assert log["target_id"] == 5
    assert log["target_type"] == "user"
    assert log["timestamp"] is not None


def test_get_audit_logs_limit():
    """Test limiting audit log results."""
    # Create 10 logs
    for i in range(10):
        log_action(AuditAction.LOGIN, i, f"Login {i}")

    # Get only 3
    logs = get_audit_logs(limit=3)
    assert len(logs) == 3


def test_audit_action_enum():
    """Test AuditAction enum values."""
    assert AuditAction.LOGIN.value == "login"
    assert AuditAction.TRANSACTION_SYNC.value == "transaction_sync"
    assert AuditAction.CHALLENGE_RESOLVE.value == "challenge_resolve"
    assert AuditAction.USER_ROLE_CHANGE.value == "user_role_change"
