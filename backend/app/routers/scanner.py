# Scanner router for FlatWatch
from fastapi import APIRouter, Depends

from ..rbac import require_admin
from ..auth import User
from ..scanner import run_daily_scan, get_scan_summary


router = APIRouter(prefix="/api/scanner", tags=["Scanner"])


@router.post("/run")
async def trigger_scan(current_user: User = Depends(require_admin)):
    """
    Manually trigger the mismatch scan.
    Admin only - normally run by cron job.
    """
    result = run_daily_scan(system_user_id=current_user.id)
    return result


@router.get("/summary")
async def get_scan_summary_api(
    hours: int = 24,
    current_user: User = Depends(require_admin),
):
    """Get scan summary for the specified period."""
    return get_scan_summary(hours)
