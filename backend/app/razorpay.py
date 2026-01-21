# Razorpay integration for FlatWatch (POC mock)
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import random

from .database import get_db_connection
from .models import Transaction, TransactionCreate


class RazorpayTransaction:
    """Mock Razorpay transaction data."""

    def __init__(
        self,
        amount: float,
        vpa: str,
        narration: str,
        txn_type: str = "inflow",
    ):
        self.amount = amount
        self.vpa = vpa
        self.narration = narration
        self.txn_type = txn_type
        self.timestamp = datetime.now(timezone.utc)


# Mock Razorpay API response
MOCK_RAZORPAY_TRANSACTIONS = [
    RazorpayTransaction(
        amount=6000.0,
        vpa="resident1@upi",
        narration="Maintenance - January",
        txn_type="inflow",
    ),
    RazorpayTransaction(
        amount=6500.0,
        vpa="resident2@upi",
        narration="Maintenance - January",
        txn_type="inflow",
    ),
    RazorpayTransaction(
        amount=8500.0,
        vpa="society@upi",
        narration="Water bill payment",
        txn_type="outflow",
    ),
    RazorpayTransaction(
        amount=15000.0,
        vpa="society@upi",
        narration="Lift maintenance",
        txn_type="outflow",
    ),
]


class RazorpayClient:
    """Mock Razorpay client for POC."""

    def __init__(self, api_key: str = None, api_secret: str = None):
        """Initialize client (POC: no credentials needed)."""
        self.api_key = api_key or "mock_key"
        self.api_secret = api_secret or "mock_secret"

    async def fetch_transactions(
        self,
        count: int = 10,
        skip: int = 0,
    ) -> List[RazorpayTransaction]:
        """
        Fetch transactions from Razorpay (POC mock).
        In production, this will call Razorpay API.
        """
        # Return mock transactions with slight randomization
        transactions = []
        for txn in MOCK_RAZORPAY_TRANSACTIONS:
            # Add slight time variation
            txn_with_time = RazorpayTransaction(
                amount=txn.amount,
                vpa=txn.vpa,
                narration=txn.narration,
                txn_type=txn.txn_type,
            )
            txn_with_time.timestamp = datetime.now(timezone.utc) - timedelta(
                minutes=random.randint(1, 60)
            )
            transactions.append(txn_with_time)

        return transactions[:count]

    async def get_payment_details(self, payment_id: str) -> Optional[dict]:
        """Get payment details by ID (POC mock)."""
        return {
            "id": payment_id,
            "amount": 600000,  # in paise
            "status": "captured",
            "vpa": "resident1@upi",
        }


async def poll_razorpay_transactions() -> List[TransactionCreate]:
    """
    Poll Razorpay for new transactions (POC mock).
    In production, this will query Razorpay API every 5 minutes.
    """
    client = RazorpayClient()
    razorpay_txns = await client.fetch_transactions(count=10)

    transactions = []
    for txn in razorpay_txns:
        transactions.append(
            TransactionCreate(
                amount=txn.amount,
                transaction_type=txn.txn_type,
                description=txn.narration,
                vpa=txn.vpa,
            )
        )

    return transactions


async def save_transactions(transactions: List[TransactionCreate]) -> int:
    """Save transactions to database."""
    conn = get_db_connection()
    saved_count = 0

    for txn in transactions:
        # Check for duplicates by VPA and amount and recent timestamp
        cursor = conn.execute(
            """
            SELECT id FROM transactions
            WHERE vpa = ? AND amount = ?
            AND datetime(timestamp) > datetime('now', '-1 hour')
            """,
            (txn.vpa, txn.amount),
        )

        if cursor.fetchone() is None:
            conn.execute(
                """
                INSERT INTO transactions (amount, transaction_type, description, vpa)
                VALUES (?, ?, ?, ?)
                """,
                (txn.amount, txn.transaction_type, txn.description, txn.vpa),
            )
            saved_count += 1

    conn.commit()
    conn.close()
    return saved_count


async def sync_transactions() -> dict:
    """
    Main sync function: poll and save new transactions.
    Returns summary of sync operation.
    """
    transactions = await poll_razorpay_transactions()
    saved = await save_transactions(transactions)

    return {
        "polled": len(transactions),
        "saved": saved,
        "skipped": len(transactions) - saved,
    }
