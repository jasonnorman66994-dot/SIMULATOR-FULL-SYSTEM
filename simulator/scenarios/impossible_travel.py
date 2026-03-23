"""
Impossible-travel scenario – login from two distant locations in minutes.
"""

from __future__ import annotations

import time
from typing import Any


def impossible_travel_scenario(user: str = "bob") -> list[dict[str, Any]]:
    """Return events simulating an impossible-travel anomaly."""
    return [
        {
            "event": "suspicious_login",
            "type": "impossible_travel",
            "user": user,
            "ip": "10.0.0.1",
            "location": "New York, USA",
            "severity": "medium",
            "timestamp": time.time(),
        },
        {
            "event": "suspicious_login",
            "type": "impossible_travel",
            "user": user,
            "ip": "203.0.113.99",
            "location": "Beijing, China",
            "severity": "high",
            "timestamp": time.time() + 120,  # 2 minutes later
        },
    ]
