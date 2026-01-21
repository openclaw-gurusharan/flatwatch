# Notifications router for FlatWatch
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..rbac import require_admin
from ..auth import User
from ..notifications import (
    NotificationFrequency,
    send_summary_email,
    send_daily_summaries,
    send_weekly_summaries,
    EmailService,
)


class SendSummaryRequest(BaseModel):
    email: str
    frequency: str  # "daily" or "weekly"


router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.post("/send")
async def send_notification_summary(
    request: SendSummaryRequest,
    current_user: User = Depends(require_admin),
):
    """
    Send a summary email to a specific user.
    Admin only.
    """
    try:
        frequency = NotificationFrequency(request.frequency)
        success = send_summary_email(request.email, frequency)
        return {
            "success": success,
            "email": request.email,
            "frequency": request.frequency,
        }
    except ValueError as e:
        return {"success": False, "error": str(e)}


@router.post("/send/daily")
async def trigger_daily_summaries(current_user: User = Depends(require_admin)):
    """
    Manually trigger daily summary emails to all users.
    Admin only - normally run by cron job.
    """
    result = send_daily_summaries()
    return result


@router.post("/send/weekly")
async def trigger_weekly_summaries(current_user: User = Depends(require_admin)):
    """
    Manually trigger weekly summary emails to all users.
    Admin only - normally run by cron job.
    """
    result = send_weekly_summaries()
    return result


@router.get("/sent")
async def get_sent_notifications(current_user: User = Depends(require_admin)):
    """
    Get list of sent notification emails (for testing/monitoring).
    Admin only.
    """
    return {"emails": EmailService.get_sent_emails()}


@router.post("/sent/clear")
async def clear_sent_notifications(current_user: User = Depends(require_admin)):
    """
    Clear sent notifications (for testing).
    Admin only.
    """
    EmailService.clear_sent_emails()
    return {"message": "Sent notifications cleared"}
