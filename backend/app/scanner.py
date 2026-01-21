# Automated mismatch scanner for FlatWatch
# Runs daily via cron to flag transaction-receipt mismatches
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from dataclasses import dataclass

from .database import get_db_connection
from .audit import AuditAction, log_action


@dataclass
class MismatchResult:
    """Result of a mismatch check."""
    transaction_id: int
    receipt_id: Optional[int]
    mismatch_type: str  # amount, date, vendor, missing_receipt
    severity: str  # red, yellow, green
    description: str
    suggested_action: str


class TransactionScanner:
    """Scans transactions for potential mismatches."""

    def __init__(self):
        self.mismatches: List[MismatchResult] = []

    def scan_all_transactions(self) -> List[MismatchResult]:
        """
        Scan all transactions for mismatches.

        Returns:
            List of mismatches found.
        """
        conn = get_db_connection()

        # Get all transactions
        cursor = conn.execute("""
            SELECT id, amount, description, transaction_type, timestamp, verified, receipt_path
            FROM transactions
            ORDER BY timestamp DESC
        """)
        transactions = cursor.fetchall()
        conn.close()

        self.mismatches = []
        for txn in transactions:
            txn_dict = dict(txn)
            self._check_transaction(txn_dict)

        return self.mismatches

    def _check_transaction(self, txn: dict) -> None:
        """Check a single transaction for mismatches."""
        txn_id = txn["id"]
        amount = txn["amount"]
        description = txn["description"]
        txn_type = txn["transaction_type"]
        receipt_path = txn.get("receipt_path")

        has_red_flag = False

        # Check 1: Outflows without receipts (Red)
        if txn_type == "outflow" and not receipt_path:
            self.mismatches.append(MismatchResult(
                transaction_id=txn_id,
                receipt_id=None,
                mismatch_type="missing_receipt",
                severity="red",
                description=f"Outflow of ₹{amount} has no supporting receipt",
                suggested_action="Request receipt from treasurer or flag as suspicious"
            ))
            has_red_flag = True

        # Check 2: Large amounts without verification (Yellow)
        # Still check even if missing receipt
        if amount > 10000 and not txn["verified"]:
            self.mismatches.append(MismatchResult(
                transaction_id=txn_id,
                receipt_id=receipt_path,
                mismatch_type="unverified_large_amount",
                severity="yellow",
                description=f"Large amount ₹{amount} not verified",
                suggested_action="Admin should verify this transaction"
            ))

        # Check 3: Suspicious descriptions
        suspicious_keywords = ["cash", "personal", "transfer", "unknown"]
        if description and any(kw in description.lower() for kw in suspicious_keywords):
            self.mismatches.append(MismatchResult(
                transaction_id=txn_id,
                receipt_id=receipt_path,
                mismatch_type="suspicious_description",
                severity="yellow",
                description=f"Transaction contains suspicious keyword: {description}",
                suggested_action="Review transaction details and evidence"
            ))

        # Check 4: Duplicate detection (same amount within 1 hour)
        if self._is_duplicate(txn):
            self.mismatches.append(MismatchResult(
                transaction_id=txn_id,
                receipt_id=receipt_path,
                mismatch_type="potential_duplicate",
                severity="yellow",
                description=f"Possible duplicate transaction: ₹{amount}",
                suggested_action="Verify if this is a legitimate duplicate payment"
            ))

    def _is_duplicate(self, txn: dict) -> bool:
        """Check if transaction might be a duplicate."""
        conn = get_db_connection()
        # Look back 1 hour from the transaction timestamp
        txn_time = datetime.fromisoformat(txn["timestamp"])
        cutoff = txn_time - timedelta(hours=1)

        cursor = conn.execute("""
            SELECT COUNT(*) as count
            FROM transactions
            WHERE amount = ? AND id != ? AND timestamp > ?
        """, (txn["amount"], txn["id"], cutoff.isoformat()))
        count = cursor.fetchone()["count"]
        conn.close()

        return count > 0


def run_daily_scan(system_user_id: int = 1) -> dict:
    """
    Run the daily mismatch scan (called by cron job).

    Args:
        system_user_id: User ID to attribute the scan to

    Returns:
        Summary of scan results
    """
    scanner = TransactionScanner()
    mismatches = scanner.scan_all_transactions()

    # Categorize by severity
    red_count = sum(1 for m in mismatches if m.severity == "red")
    yellow_count = sum(1 for m in mismatches if m.severity == "yellow")

    # Log the scan
    log_action(
        AuditAction.CONFIG_UPDATE,
        system_user_id,
        f"Daily scan completed: {len(mismatches)} mismatches found ({red_count} red, {yellow_count} yellow)",
    )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_mismatches": len(mismatches),
        "red_flags": red_count,
        "yellow_flags": yellow_count,
        "mismatches": [
            {
                "transaction_id": m.transaction_id,
                "type": m.mismatch_type,
                "severity": m.severity,
                "description": m.description,
                "suggested_action": m.suggested_action,
            }
            for m in mismatches
        ]
    }


def get_scan_summary(hours: int = 24) -> dict:
    """
    Get summary of recent scans.

    Args:
        hours: Number of hours to look back
    """
    conn = get_db_connection()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    # Get transactions flagged in recent period
    cursor = conn.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN transaction_type = 'outflow' AND receipt_path IS NULL THEN 1 ELSE 0 END) as missing_receipts,
               SUM(CASE WHEN amount > 10000 AND verified = 0 THEN 1 ELSE 0 END) as unverified_large
        FROM transactions
        WHERE datetime(timestamp) > ?
    """, (cutoff.isoformat(),))

    stats = cursor.fetchone()
    conn.close()

    return {
        "period_hours": hours,
        "total_transactions": stats["total"],
        "missing_receipts": stats["missing_receipts"],
        "unverified_large_amounts": stats["unverified_large"],
    }
