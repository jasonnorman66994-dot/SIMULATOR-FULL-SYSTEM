"""
Phishing scenario – a realistic multi-step attack chain.

Produces a sequence of correlated events that a SOC analyst would see during
a real spear-phishing attack.
"""

from __future__ import annotations

from typing import Any

import time


def phishing_scenario(user: str = "alice", attacker_ip: str = "8.8.8.8") -> list[dict[str, Any]]:
    """Return an ordered list of events representing a phishing attack chain."""
    return [
        {
            "event": "email_delivered",
            "type": "email_delivered",
            "user": user,
            "ip": attacker_ip,
            "severity": "low",
            "timestamp": time.time(),
        },
        {
            "event": "link_clicked",
            "type": "link_clicked",
            "user": user,
            "ip": attacker_ip,
            "severity": "medium",
            "timestamp": time.time(),
        },
        {
            "event": "credential_entered",
            "type": "credential_entered",
            "user": user,
            "ip": attacker_ip,
            "severity": "high",
            "timestamp": time.time(),
        },
        {
            "event": "suspicious_login",
            "type": "suspicious_login",
            "user": user,
            "ip": attacker_ip,
            "severity": "high",
            "timestamp": time.time(),
        },
    ]
