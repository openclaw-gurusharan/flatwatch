# Tests for automated mismatch scanner
import pytest
from datetime import datetime, timezone, timedelta

from app.scanner import (
    TransactionScanner,
    MismatchResult,
    run_daily_scan,
    get_scan_summary,
)
from app.database import init_db, get_db_connection, get_db_path
import os


@pytest.fixture(autouse=True)
def setup_database():
    """Initialize database before each test."""
    init_db()
    yield
    db_path = get_db_path()
    if db_path.exists():
        os.remove(db_path)


def test_scanner_initially_empty():
    """Scanner returns no mismatches for empty database."""
    scanner = TransactionScanner()
    mismatches = scanner.scan_all_transactions()
    assert len(mismatches) == 0


def test_scanner_detects_missing_receipts():
    """Scanner detects outflows without receipts."""
    conn = get_db_connection()
    # Create outflow without receipt
    conn.execute(
        """
        INSERT INTO transactions (amount, transaction_type, description, timestamp)
        VALUES (5000, 'outflow', 'Test payment', ?)
        """,
        (datetime.now(timezone.utc).isoformat(),),
    )
    conn.commit()
    conn.close()

    scanner = TransactionScanner()
    mismatches = scanner.scan_all_transactions()

    assert len(mismatches) == 1
    assert mismatches[0].mismatch_type == "missing_receipt"
    assert mismatches[0].severity == "red"


def test_scanner_detects_unverified_large_amounts():
    """Scanner flags large unverified amounts."""
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO transactions (amount, transaction_type, description, verified, timestamp)
        VALUES (15000, 'outflow', 'Large payment', 0, ?)
        """,
        (datetime.now(timezone.utc).isoformat(),),
    )
    conn.commit()
    conn.close()

    scanner = TransactionScanner()
    mismatches = scanner.scan_all_transactions()

    assert any(m.mismatch_type == "unverified_large_amount" for m in mismatches)


def test_scanner_detects_suspicious_keywords():
    """Scanner detects suspicious keywords in descriptions."""
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO transactions (amount, transaction_type, description, timestamp)
        VALUES (1000, 'outflow', 'Personal cash withdrawal', ?)
        """,
        (datetime.now(timezone.utc).isoformat(),),
    )
    conn.commit()
    conn.close()

    scanner = TransactionScanner()
    mismatches = scanner.scan_all_transactions()

    assert any(m.mismatch_type == "suspicious_description" for m in mismatches)


def test_scanner_detects_potential_duplicates():
    """Scanner detects potential duplicate transactions."""
    conn = get_db_connection()
    now = datetime.now(timezone.utc)
    # Two transactions with same amount within 1 hour - add receipt path to avoid missing_receipt flag
    conn.execute(
        """
        INSERT INTO transactions (amount, transaction_type, description, timestamp, receipt_path)
        VALUES (5000, 'outflow', 'Payment 1', ?, 'receipt1.pdf')
        """,
        (now.isoformat(),),
    )
    conn.execute(
        """
        INSERT INTO transactions (amount, transaction_type, description, timestamp, receipt_path)
        VALUES (5000, 'outflow', 'Payment 2', ?, 'receipt2.pdf')
        """,
        ((now + timedelta(minutes=30)).isoformat(),),
    )
    conn.commit()
    conn.close()

    scanner = TransactionScanner()
    mismatches = scanner.scan_all_transactions()

    assert any(m.mismatch_type == "potential_duplicate" for m in mismatches)


def test_run_daily_scan():
    """Test running daily scan."""
    # Add some test data
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO transactions (amount, transaction_type, description, timestamp)
        VALUES (5000, 'outflow', 'Test', ?)
        """,
        (datetime.now(timezone.utc).isoformat(),),
    )
    conn.commit()
    conn.close()

    result = run_daily_scan(system_user_id=1)

    assert "timestamp" in result
    assert "total_mismatches" in result
    assert "red_flags" in result
    assert "yellow_flags" in result
    assert result["total_mismatches"] > 0


def test_get_scan_summary():
    """Test getting scan summary."""
    # Add test data
    conn = get_db_connection()
    now = datetime.now(timezone.utc)
    conn.execute(
        """
        INSERT INTO transactions (amount, transaction_type, description, timestamp)
        VALUES (5000, 'outflow', 'Test', ?)
        """,
        (now.isoformat(),),
    )
    conn.commit()
    conn.close()

    summary = get_scan_summary(hours=24)

    assert summary["period_hours"] == 24
    assert summary["total_transactions"] >= 1


def test_mismatch_result_dataclass():
    """Test MismatchResult dataclass."""
    result = MismatchResult(
        transaction_id=1,
        receipt_id=None,
        mismatch_type="missing_receipt",
        severity="red",
        description="Test",
        suggested_action="Fix it"
    )

    assert result.transaction_id == 1
    assert result.severity == "red"
    assert result.suggested_action == "Fix it"


def test_scanner_ignores_inflows_without_receipts():
    """Inflows without receipts are not flagged (only outflows)."""
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO transactions (amount, transaction_type, description, timestamp)
        VALUES (5000, 'inflow', 'Maintenance collection', ?)
        """,
        (datetime.now(timezone.utc).isoformat(),),
    )
    conn.commit()
    conn.close()

    scanner = TransactionScanner()
    mismatches = scanner.scan_all_transactions()

    # Inflows without receipts are OK
    assert not any(m.mismatch_type == "missing_receipt" for m in mismatches)


def test_scanner_ignores_verified_amounts():
    """Verified large amounts are not flagged."""
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO transactions (amount, transaction_type, description, verified, timestamp)
        VALUES (15000, 'outflow', 'Verified large payment', 1, ?)
        """,
        (datetime.now(timezone.utc).isoformat(),),
    )
    conn.commit()
    conn.close()

    scanner = TransactionScanner()
    mismatches = scanner.scan_all_transactions()

    assert not any(m.mismatch_type == "unverified_large_amount" for m in mismatches)
