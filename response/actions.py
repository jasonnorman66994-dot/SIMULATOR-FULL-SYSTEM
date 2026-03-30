"""
Response actions module.

All functions accept a *simulation_mode* flag (defaults to the global
``config.SIMULATION_MODE``).  When ``True`` the action is **logged but not
executed** against real infrastructure, making it completely safe for demos
and development environments.
"""

from __future__ import annotations

import time
from typing import Any

from compliance import logger as audit
from config import SIMULATION_MODE


def _record(action: str, target: str, reason: str, simulated: bool) -> dict[str, Any]:
    """Build a response result dict and write it to the audit log."""
    result: dict[str, Any] = {
        "action": action,
        "target": target,
        "reason": reason,
        "simulated": simulated,
        "timestamp": time.time(),
        "status": "simulated" if simulated else "executed",
    }
    audit.log_action(action, result)
    return result


def block_ip(ip: str, reason: str = "", *, simulation_mode: bool = SIMULATION_MODE) -> dict[str, Any]:
    """Block an IP address at the perimeter firewall."""
    if not simulation_mode:
        # TODO: call real firewall / WAF API here
        pass
    tag = "[SIMULATION] " if simulation_mode else ""
    print(f"{tag}block_ip  → {ip}  ({reason})")
    return _record("block_ip", ip, reason, simulation_mode)


def revoke_session(user: str, reason: str = "", *, simulation_mode: bool = SIMULATION_MODE) -> dict[str, Any]:
    """Revoke all active sessions for a user."""
    if not simulation_mode:
        # TODO: call real IAM / session store here
        pass
    tag = "[SIMULATION] " if simulation_mode else ""
    print(f"{tag}revoke_session → {user}  ({reason})")
    return _record("revoke_session", user, reason, simulation_mode)


def flag_account(user: str, reason: str = "", *, simulation_mode: bool = SIMULATION_MODE) -> dict[str, Any]:
    """Flag a user account for manual review."""
    if not simulation_mode:
        # TODO: call real user-management API here
        pass
    tag = "[SIMULATION] " if simulation_mode else ""
    print(f"{tag}flag_account  → {user}  ({reason})")
    return _record("flag_account", user, reason, simulation_mode)


def isolate_device(user: str, reason: str = "", *, simulation_mode: bool = SIMULATION_MODE) -> dict[str, Any]:
    """Network-isolate the device associated with a user session."""
    if not simulation_mode:
        # TODO: call real EDR / NAC API here
        pass
    tag = "[SIMULATION] " if simulation_mode else ""
    print(f"{tag}isolate_device → {user}  ({reason})")
    return _record("isolate_device", user, reason, simulation_mode)


# Map recommended action names → callable
ACTION_MAP: dict[str, Any] = {
    "block_ip": block_ip,
    "revoke_session": revoke_session,
    "flag_account": flag_account,
    "isolate_device": isolate_device,
}


def execute_action(action_name: str, event: dict[str, Any], *, simulation_mode: bool = SIMULATION_MODE) -> dict[str, Any]:
    """Dispatch the named action using context extracted from *event*."""
    fn = ACTION_MAP.get(action_name)
    if fn is None:
        return {"action": action_name, "status": "unknown_action"}
    user = event.get("user", "unknown")
    ip = event.get("ip", "unknown")
    reason = f"auto-response for {event.get('type', 'unknown')} event"
    # Choose the primary target depending on the action type
    if action_name == "block_ip":
        return fn(ip, reason, simulation_mode=simulation_mode)
    return fn(user, reason, simulation_mode=simulation_mode)
