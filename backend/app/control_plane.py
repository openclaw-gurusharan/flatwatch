from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional, TypedDict

from fastapi import Request
from pydantic import BaseModel

from .database import get_db
from .runtime_config import AgentAuthMode, resolve_runtime_policy

AppId = Literal["flatwatch", "ondc-buyer", "ondc-seller"]
PortfolioTrustState = Literal[
    "no_identity",
    "identity_present_unverified",
    "verified",
    "manual_review",
    "revoked_or_blocked",
]
SessionMode = Literal["blocked", "read_only", "full"]


class UsageSnapshot(BaseModel):
    requests_used: int
    requests_limit: int
    period_start: str
    period_end: str
    estimated_cost_usd: float


class AgentRuntimeSnapshot(BaseModel):
    app_id: AppId
    auth_mode: AgentAuthMode
    model: str
    runtime_available: bool
    agent_access: bool
    trust_state: PortfolioTrustState
    trust_required_for_write: bool
    mode: SessionMode
    usage: UsageSnapshot
    allowed_capabilities: list[str]
    blocked_reason: Optional[str] = None


class AgentSessionSummary(BaseModel):
    app_id: AppId
    session_id: str
    sdk_session_id: Optional[str] = None
    subject_id: str
    trust_state: PortfolioTrustState
    mode: SessionMode
    allowed_capabilities: list[str]
    created_at: str
    updated_at: str


class AgentSessionCreateRequest(BaseModel):
    task_type: str
    context: dict[str, Any]
    resume_session_id: Optional[str] = None


class AgentMessageRequest(BaseModel):
    session_id: str
    message: str


class StoredUsageRecord(TypedDict):
    subject_id: str
    app_id: AppId
    requests_used: int
    requests_limit: int
    period_start: str
    period_end: str
    estimated_cost_usd: float


class StoredSessionRecord(TypedDict):
    session_id: str
    app_id: AppId
    user_id: int
    subject_id: str
    wallet_address: Optional[str]
    sdk_session_id: Optional[str]
    trust_state: PortfolioTrustState
    mode: SessionMode
    allowed_capabilities: list[str]
    task_type: str
    context: dict[str, Any]
    messages: list[dict[str, Any]]
    created_at: str
    updated_at: str


APP_CAPABILITIES: dict[AppId, dict[str, list[str]]] = {
    "flatwatch": {
        "read": ["transactions_query", "receipts_metadata", "challenges_summary", "bylaw_lookup"],
        "write": ["receipt_process_metadata", "challenge_create", "challenge_resolve"],
    },
    "ondc-buyer": {
        "read": ["search", "product_detail", "cart_state", "order_status", "trust_checkout_guidance"],
        "write": ["checkout_mutation"],
    },
    "ondc-seller": {
        "read": ["catalog_read", "listing_quality_analysis", "order_status", "seller_config_guidance"],
        "write": ["catalog_write", "listing_publish"],
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_period_end() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()


def _default_usage(subject_id: str, app_id: AppId) -> StoredUsageRecord:
    return {
        "subject_id": subject_id,
        "app_id": app_id,
        "requests_used": 0,
        "requests_limit": 0,
        "period_start": _now_iso(),
        "period_end": _default_period_end(),
        "estimated_cost_usd": 0.0,
    }


def _usage_from_row(row: Any) -> StoredUsageRecord:
    return {
        "subject_id": row["subject_id"],
        "app_id": row["app_id"],
        "requests_used": int(row["requests_used"]),
        "requests_limit": int(row["requests_limit"]),
        "period_start": row["period_start"],
        "period_end": row["period_end"],
        "estimated_cost_usd": float(row["estimated_cost_usd"]),
    }


def _session_from_row(row: Any) -> StoredSessionRecord:
    return {
        "session_id": row["session_id"],
        "app_id": row["app_id"],
        "user_id": int(row["user_id"]),
        "subject_id": row["subject_id"],
        "wallet_address": row["wallet_address"],
        "sdk_session_id": row["sdk_session_id"],
        "trust_state": row["trust_state"],
        "mode": row["mode"],
        "allowed_capabilities": json.loads(row["allowed_capabilities"]),
        "task_type": row["task_type"],
        "context": json.loads(row["context_json"]),
        "messages": json.loads(row["messages_json"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _session_summary(record: StoredSessionRecord) -> AgentSessionSummary:
    return AgentSessionSummary(
        app_id=record["app_id"],
        session_id=record["session_id"],
        sdk_session_id=record.get("sdk_session_id"),
        subject_id=record["subject_id"],
        trust_state=record["trust_state"],
        mode=record["mode"],
        allowed_capabilities=record["allowed_capabilities"],
        created_at=record["created_at"],
        updated_at=record["updated_at"],
    )


def get_or_create_usage(subject_id: str, app_id: AppId) -> StoredUsageRecord:
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT subject_id, app_id, requests_used, requests_limit, period_start, period_end, estimated_cost_usd
            FROM agent_usage
            WHERE subject_id = ? AND app_id = ?
            """,
            (subject_id, app_id),
        ).fetchone()
        if row is not None:
            return _usage_from_row(row)

        record = _default_usage(subject_id, app_id)
        conn.execute(
            """
            INSERT INTO agent_usage (
                subject_id, app_id, requests_used, requests_limit, period_start, period_end, estimated_cost_usd
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["subject_id"],
                record["app_id"],
                record["requests_used"],
                record["requests_limit"],
                record["period_start"],
                record["period_end"],
                record["estimated_cost_usd"],
            ),
        )
        return record


def build_runtime_snapshot(
    subject_id: str,
    app_id: AppId,
    trust_state: PortfolioTrustState,
    trust_reason: Optional[str],
    request: Optional[Request] = None,
) -> AgentRuntimeSnapshot:
    usage = get_or_create_usage(subject_id, app_id)
    runtime_policy = resolve_runtime_policy(request)
    if not runtime_policy.runtime_available:
        mode: SessionMode = "blocked"
    elif trust_state == "verified":
        mode = "full"
    else:
        mode = "read_only"

    blocked_reason = runtime_policy.blocked_reason
    if blocked_reason is None and mode == "read_only":
        blocked_reason = trust_reason or "Trust verification is still required for higher-trust write actions."

    if mode == "blocked":
        allowed_capabilities: list[str] = []
    elif mode == "read_only":
        allowed_capabilities = APP_CAPABILITIES[app_id]["read"]
    else:
        allowed_capabilities = APP_CAPABILITIES[app_id]["read"] + APP_CAPABILITIES[app_id]["write"]

    return AgentRuntimeSnapshot(
        app_id=app_id,
        auth_mode=runtime_policy.auth_mode,
        model=runtime_policy.model,
        runtime_available=runtime_policy.runtime_available,
        agent_access=runtime_policy.runtime_available,
        trust_state=trust_state,
        trust_required_for_write=True,
        mode=mode,
        usage=UsageSnapshot(
            requests_used=usage["requests_used"],
            requests_limit=usage["requests_limit"],
            period_start=usage["period_start"],
            period_end=usage["period_end"],
            estimated_cost_usd=usage["estimated_cost_usd"],
        ),
        allowed_capabilities=allowed_capabilities,
        blocked_reason=blocked_reason,
    )


def record_usage(subject_id: str, app_id: AppId, incremental_cost_usd: float = 0.0) -> UsageSnapshot:
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT subject_id, app_id, requests_used, requests_limit, period_start, period_end, estimated_cost_usd
            FROM agent_usage
            WHERE subject_id = ? AND app_id = ?
            """,
            (subject_id, app_id),
        ).fetchone()

        if row is None:
            updated = _default_usage(subject_id, app_id)
            updated["requests_used"] = 1
            updated["estimated_cost_usd"] = round(incremental_cost_usd, 6)
            conn.execute(
                """
                INSERT INTO agent_usage (
                    subject_id, app_id, requests_used, requests_limit, period_start, period_end, estimated_cost_usd
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    updated["subject_id"],
                    updated["app_id"],
                    updated["requests_used"],
                    updated["requests_limit"],
                    updated["period_start"],
                    updated["period_end"],
                    updated["estimated_cost_usd"],
                ),
            )
        else:
            updated = _usage_from_row(row)
            updated["requests_used"] += 1
            updated["estimated_cost_usd"] = round(updated["estimated_cost_usd"] + incremental_cost_usd, 6)
            conn.execute(
                """
                UPDATE agent_usage
                SET requests_used = ?, estimated_cost_usd = ?
                WHERE subject_id = ? AND app_id = ?
                """,
                (
                    updated["requests_used"],
                    updated["estimated_cost_usd"],
                    subject_id,
                    app_id,
                ),
            )

    return UsageSnapshot(
        requests_used=updated["requests_used"],
        requests_limit=updated["requests_limit"],
        period_start=updated["period_start"],
        period_end=updated["period_end"],
        estimated_cost_usd=updated["estimated_cost_usd"],
    )


def save_agent_session(
    *,
    session_id: str,
    app_id: AppId,
    user_id: int,
    subject_id: str,
    wallet_address: Optional[str],
    sdk_session_id: Optional[str],
    trust_state: PortfolioTrustState,
    mode: SessionMode,
    allowed_capabilities: list[str],
    task_type: str,
    context: dict[str, Any],
    messages: list[dict[str, Any]],
) -> AgentSessionSummary:
    timestamp = _now_iso()
    with get_db() as conn:
        existing = conn.execute(
            "SELECT session_id, user_id, created_at FROM agent_sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if existing is not None and int(existing["user_id"]) != user_id:
            raise ValueError("Session belongs to a different user.")

        created_at = existing["created_at"] if existing is not None else timestamp
        conn.execute(
            """
            INSERT INTO agent_sessions (
                session_id, app_id, user_id, subject_id, wallet_address, sdk_session_id,
                trust_state, mode, allowed_capabilities, task_type, context_json, messages_json,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                app_id = excluded.app_id,
                user_id = excluded.user_id,
                subject_id = excluded.subject_id,
                wallet_address = excluded.wallet_address,
                sdk_session_id = excluded.sdk_session_id,
                trust_state = excluded.trust_state,
                mode = excluded.mode,
                allowed_capabilities = excluded.allowed_capabilities,
                task_type = excluded.task_type,
                context_json = excluded.context_json,
                messages_json = excluded.messages_json,
                updated_at = excluded.updated_at
            """,
            (
                session_id,
                app_id,
                user_id,
                subject_id,
                wallet_address,
                sdk_session_id,
                trust_state,
                mode,
                json.dumps(allowed_capabilities),
                task_type,
                json.dumps(context),
                json.dumps(messages),
                created_at,
                timestamp,
            ),
        )
        row = conn.execute(
            """
            SELECT session_id, app_id, user_id, subject_id, wallet_address, sdk_session_id,
                   trust_state, mode, allowed_capabilities, task_type, context_json, messages_json,
                   created_at, updated_at
            FROM agent_sessions
            WHERE session_id = ? AND user_id = ?
            """,
            (session_id, user_id),
        ).fetchone()

    return _session_summary(_session_from_row(row))


def get_agent_session(session_id: str, user_id: int) -> Optional[StoredSessionRecord]:
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT session_id, app_id, user_id, subject_id, wallet_address, sdk_session_id,
                   trust_state, mode, allowed_capabilities, task_type, context_json, messages_json,
                   created_at, updated_at
            FROM agent_sessions
            WHERE session_id = ? AND user_id = ?
            """,
            (session_id, user_id),
        ).fetchone()
        if row is None:
            return None
        return _session_from_row(row)
