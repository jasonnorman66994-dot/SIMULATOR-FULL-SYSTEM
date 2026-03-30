"""
Detection engine.

Evaluates incoming events against a rule set and returns a structured alert
when a rule matches.  The engine is intentionally stateless so it can be
called from any thread.
"""

from __future__ import annotations

import time
from typing import Any

# ---------------------------------------------------------------------------
# Detection rules
# Each key matches an attack ``type``; the value provides the recommended
# response action and an override severity (if different from the event).
# ---------------------------------------------------------------------------
DETECTION_RULES: dict[str, dict[str, str]] = {
    "phishing_click": {
        "severity": "high",
        "action": "revoke_session",
        "description": "User interacted with a phishing link",
    },
    "credential_stuffing": {
        "severity": "critical",
        "action": "block_ip",
        "description": "Automated credential-stuffing attack detected",
    },
    "impossible_travel": {
        "severity": "high",
        "action": "flag_account",
        "description": "Login from geographically impossible location",
    },
    "data_exfiltration": {
        "severity": "critical",
        "action": "isolate_device",
        "description": "Abnormal outbound data transfer detected",
    },
    # Scenario sub-events
    "email_delivered": {
        "severity": "low",
        "action": "flag_account",
        "description": "Phishing email delivered to mailbox",
    },
    "link_clicked": {
        "severity": "medium",
        "action": "flag_account",
        "description": "User clicked a suspicious link",
    },
    "credential_entered": {
        "severity": "high",
        "action": "revoke_session",
        "description": "Credentials entered on suspicious page",
    },
    "suspicious_login": {
        "severity": "high",
        "action": "block_ip",
        "description": "Login from suspicious IP address",
    },
}


def detect(event: dict[str, Any]) -> dict[str, Any]:
    """
    Evaluate *event* against the detection rule set.

    Returns a dict with ``alert=True`` and enriched metadata when a rule
    matches, or ``alert=False`` when no rule is triggered.
    """
    attack_type: str = event.get("type") or event.get("event") or ""
    rule = DETECTION_RULES.get(attack_type)

    if rule is None:
        return {"alert": False, "event": event, "timestamp": time.time()}

    return {
        "alert": True,
        "rule_matched": attack_type,
        "description": rule["description"],
        "recommended_action": rule["action"],
        "severity": rule.get("severity", event.get("severity", "medium")),
        "event": event,
        "timestamp": time.time(),
    }
