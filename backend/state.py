"""
Shared in-process state for the FastAPI backend.

All modules import from here so there is a single source of truth for the
live alert list, stats counters, and WebSocket connection pool.
"""

from __future__ import annotations

import threading
from typing import Any

from fastapi import WebSocket

_lock = threading.Lock()

# Live alerts list (last 200 kept in memory)
alerts: list[dict[str, Any]] = []
MAX_ALERTS = 200

# Real-time stats
stats: dict[str, int] = {
    "attacks_per_min": 0,
    "ai_actions": 0,
    "threats_blocked": 0,
}

# WebSocket connection pool
_connections: list[WebSocket] = []


def add_alert(alert: dict[str, Any]) -> None:
    with _lock:
        alerts.append(alert)
        if len(alerts) > MAX_ALERTS:
            alerts.pop(0)
        if alert.get("severity") in ("high", "critical"):
            stats["threats_blocked"] += 1
        stats["attacks_per_min"] += 1


def get_alerts(limit: int = 50) -> list[dict[str, Any]]:
    with _lock:
        return list(alerts[-limit:])


def increment_ai_actions() -> None:
    with _lock:
        stats["ai_actions"] += 1


def get_stats() -> dict[str, int]:
    with _lock:
        return dict(stats)


def reset() -> None:
    """Clear all state (useful for demo resets)."""
    with _lock:
        alerts.clear()
        stats["attacks_per_min"] = 0
        stats["ai_actions"] = 0
        stats["threats_blocked"] = 0


def register_ws(ws: WebSocket) -> None:
    with _lock:
        _connections.append(ws)


def unregister_ws(ws: WebSocket) -> None:
    with _lock:
        if ws in _connections:
            _connections.remove(ws)


def get_connections() -> list[WebSocket]:
    with _lock:
        return list(_connections)
