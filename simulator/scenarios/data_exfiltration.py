"""
Data-exfiltration scenario – abnormal outbound data transfer.
"""

from __future__ import annotations

import time
from typing import Any


def data_exfiltration_scenario(user: str = "charlie", c2_ip: str = "198.51.100.77") -> list[dict[str, Any]]:
    """Return events simulating a data-exfiltration attempt."""
    return [
        {
            "event": "suspicious_login",
            "type": "suspicious_login",
            "user": user,
            "ip": c2_ip,
            "severity": "high",
            "timestamp": time.time(),
        },
        {
            "event": "data_exfiltration",
            "type": "data_exfiltration",
            "user": user,
            "ip": c2_ip,
            "bytes_transferred": 524288000,  # 500 MB
            "destination": c2_ip,
            "severity": "critical",
            "timestamp": time.time() + 30,
        },
    ]
