"""
Credential-stuffing scenario – automated large-scale login attacks.
"""

from __future__ import annotations

import random
import time
from typing import Any

_ATTACKER_IPS = ["203.0.113.5", "198.51.100.22", "192.0.2.47"]
_USERS = ["alice", "bob", "charlie", "david", "eve"]


def credential_stuffing_scenario(attacker_ip: str | None = None) -> list[dict[str, Any]]:
    """Return a sequence of events simulating a credential-stuffing campaign."""
    ip = attacker_ip or random.choice(_ATTACKER_IPS)
    events: list[dict[str, Any]] = []
    # Multiple rapid login attempts across different accounts
    for user in random.sample(_USERS, k=3):
        events.append(
            {
                "event": "credential_stuffing",
                "type": "credential_stuffing",
                "user": user,
                "ip": ip,
                "severity": "critical",
                "timestamp": time.time(),
            }
        )
    return events
