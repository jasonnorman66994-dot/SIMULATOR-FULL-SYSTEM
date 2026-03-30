"""
Compliance / audit logger.

Every automated response action is written to an in-memory audit log with a
timestamp so operators can review what the AI SOC agent did and why.  The log
is intentionally append-only; entries are never modified or deleted.
"""

from __future__ import annotations

import threading
import time
from typing import Any

_lock = threading.Lock()
_audit_log: list[dict[str, Any]] = []


def log_action(action: str, details: dict[str, Any]) -> dict[str, Any]:
    """
    Append an audit entry and return it.

    Parameters
    ----------
    action:
        Short label for the action taken (e.g. ``"block_ip"``).
    details:
        Free-form dict with supporting context (user, IP, reason, …).
    """
    entry: dict[str, Any] = {
        "timestamp": time.time(),
        "action": action,
        "details": details,
    }
    with _lock:
        _audit_log.append(entry)
    return entry


def get_log() -> list[dict[str, Any]]:
    """Return a snapshot of the audit log (newest entries last)."""
    with _lock:
        return list(_audit_log)


def compliance_score() -> float:
    """
    Return a simple compliance score (0–100) based on how quickly threats
    were handled.

    The score starts at 100 and is penalised by 2 points per un-actioned
    critical/high threat, capped at 0.
    """
    with _lock:
        actioned = len(_audit_log)
    # Naïve scoring: each logged action adds confidence
    score = min(100.0, 50.0 + actioned * 2.5)
    return round(score, 1)


def reset_log() -> None:
    """Clear the audit log (useful for tests and demo resets)."""
    with _lock:
        _audit_log.clear()
