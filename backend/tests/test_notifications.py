# Tests for email notifications (POC mock)
import pytest
from datetime import datetime, timezone

from app.notifications import (
    EmailService,
    NotificationFrequency,
    generate_summary_html,
    generate_summary_text,
    get_summary_data,
    send_summary_email,
    send_daily_summaries,
    send_weekly_summaries,
    EmailSummary,
)
from app.database import init_db, get_db_path
import os


@pytest.fixture(autouse=True)
def setup_database():
    """Initialize database before each test."""
    init_db()
    yield
    # Clear sent emails between tests
    EmailService.clear_sent_emails()
    db_path = get_db_path()
    if db_path.exists():
        os.remove(db_path)


def test_email_service_send_email():
    """Test sending email (POC mock)."""
    EmailService.clear_sent_emails()
    result = EmailService.send_email(
        to="test@example.com",
        subject="Test Subject",
        html_body="<p>Test HTML</p>",
        text_body="Test Text"
    )

    assert result is True
    emails = EmailService.get_sent_emails()
    assert len(emails) == 1
    assert emails[0]["to"] == "test@example.com"
    assert emails[0]["subject"] == "Test Subject"


def test_email_service_clear_emails():
    """Test clearing sent emails."""
    EmailService.send_email("test@example.com", "Test", "HTML", "Text")
    assert len(EmailService.get_sent_emails()) == 1

    EmailService.clear_sent_emails()
    assert len(EmailService.get_sent_emails()) == 0


def test_generate_summary_html():
    """Test HTML email generation."""
    summary = EmailSummary(
        recipient_email="test@example.com",
        recipient_name="Test User",
        frequency="daily",
        period_start="2026-01-01T00:00:00+00:00",
        period_end="2026-01-02T00:00:00+00:00",
        balance=100000,
        total_inflow=50000,
        total_outflow=30000,
        transaction_count=10,
        pending_challenges=2,
        red_flags=1,
        yellow_flags=3,
    )

    html = generate_summary_html(summary)

    assert "Test User" in html
    assert "₹100,000" in html or "100000" in html
    assert "daily" in html
    assert "<html>" in html


def test_generate_summary_text():
    """Test plain text email generation."""
    summary = EmailSummary(
        recipient_email="test@example.com",
        recipient_name="Test User",
        frequency="weekly",
        period_start="2026-01-01T00:00:00+00:00",
        period_end="2026-01-08T00:00:00+00:00",
        balance=50000,
        total_inflow=25000,
        total_outflow=15000,
        transaction_count=5,
        pending_challenges=1,
        red_flags=0,
        yellow_flags=2,
    )

    text = generate_summary_text(summary)

    assert "Test User" in text
    assert "50,000" in text or "50000" in text
    assert "WEEKLY" in text.upper()


def test_get_summary_data():
    """Test getting summary data for user."""
    summary = get_summary_data("admin@flatwatch.test", NotificationFrequency.DAILY)

    assert summary.recipient_email == "admin@flatwatch.test"
    assert summary.frequency == "daily"
    assert summary.balance >= 0


def test_send_summary_email():
    """Test sending summary email to user."""
    EmailService.clear_sent_emails()
    success = send_summary_email("admin@flatwatch.test", NotificationFrequency.DAILY)

    assert success is True
    emails = EmailService.get_sent_emails()
    assert len(emails) == 1
    assert "Financial Summary" in emails[0]["subject"]


def test_send_daily_summaries():
    """Test sending daily summaries to all users."""
    EmailService.clear_sent_emails()
    result = send_daily_summaries()

    assert result["sent"] > 0
    assert len(EmailService.get_sent_emails()) > 0


def test_send_weekly_summaries():
    """Test sending weekly summaries to all users."""
    EmailService.clear_sent_emails()
    result = send_weekly_summaries()

    assert result["sent"] > 0
    assert len(EmailService.get_sent_emails()) > 0


def test_notification_frequency_enum():
    """Test NotificationFrequency enum."""
    assert NotificationFrequency.DAILY.value == "daily"
    assert NotificationFrequency.WEEKLY.value == "weekly"


def test_summary_email_contains_metrics():
    """Test summary email contains all required metrics."""
    EmailService.clear_sent_emails()
    send_summary_email("admin@flatwatch.test", NotificationFrequency.DAILY)

    emails = EmailService.get_sent_emails()
    email = emails[0]

    assert "Financial Summary" in email["subject"]
    assert email["status"] == "sent"
    assert "timestamp" in email


def test_invalid_user_raises_error():
    """Test sending to invalid user raises error."""
    with pytest.raises(ValueError):
        get_summary_data("invalid@example.com", NotificationFrequency.DAILY)


def test_summary_with_transactions():
    """Test summary includes transaction data."""
    from app.database import get_db_connection

    # Add test transaction
    conn = get_db_connection()
    conn.execute(
        """
        INSERT INTO transactions (amount, transaction_type, description, timestamp)
        VALUES (5000, 'inflow', 'Test payment', ?)
        """,
        (datetime.now(timezone.utc).isoformat(),),
    )
    conn.commit()
    conn.close()

    summary = get_summary_data("admin@flatwatch.test", NotificationFrequency.DAILY)

    assert summary.transaction_count >= 1
