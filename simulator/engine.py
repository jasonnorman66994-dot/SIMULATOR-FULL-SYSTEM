"""
Attack simulator engine.

Runs in its own background thread, periodically generating realistic attack
events and feeding them into the ingestion pipeline.  A companion
``run_scenario`` function replays a scripted multi-step scenario.
"""

from __future__ import annotations

import random
import threading
import time
from typing import Any

from config import SIMULATOR_INTERVAL_SECONDS, SCENARIO_STEP_DELAY_SECONDS
from ingestion.producer import send_log

ATTACK_TYPES: list[str] = [
    "phishing_click",
    "credential_stuffing",
    "impossible_travel",
    "data_exfiltration",
]

USERS: list[str] = ["alice", "bob", "charlie", "david", "eve"]

# ---------------------------------------------------------------------------
# Module-level state (thread-safe)
# ---------------------------------------------------------------------------
_running = threading.Event()
_thread: threading.Thread | None = None
_lock = threading.Lock()


def generate_attack() -> dict[str, Any]:
    """Return a randomly generated attack event."""
    attack = random.choice(ATTACK_TYPES)
    return {
        "type": attack,
        "event": attack,
        "user": random.choice(USERS),
        "ip": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
        "severity": random.choice(["low", "medium", "high", "critical"]),
        "timestamp": time.time(),
    }


def _loop(interval: float) -> None:
    """Internal worker loop – sends events until stopped."""
    while _running.is_set():
        event = generate_attack()
        print("[SIMULATED ATTACK]", event)
        send_log(event)
        time.sleep(interval)


def start(interval: float = SIMULATOR_INTERVAL_SECONDS) -> bool:
    """
    Start the simulator background thread.

    Returns ``True`` if the simulator was started, ``False`` if it was already
    running.
    """
    global _thread  # noqa: PLW0603
    with _lock:
        if _running.is_set():
            return False
        _running.set()
        _thread = threading.Thread(target=_loop, args=(interval,), daemon=True, name="simulator")
        _thread.start()
    return True


def stop() -> bool:
    """
    Stop the simulator background thread.

    Returns ``True`` if the simulator was stopped, ``False`` if it was not
    running.
    """
    with _lock:
        if not _running.is_set():
            return False
        _running.clear()
    return True


def is_running() -> bool:
    """Return ``True`` if the simulator is currently active."""
    return _running.is_set()


# ---------------------------------------------------------------------------
# Scenario replay
# ---------------------------------------------------------------------------

def run_scenario(events: list[dict[str, Any]], delay: float = SCENARIO_STEP_DELAY_SECONDS) -> None:
    """
    Replay a scripted event sequence with a fixed *delay* between steps.

    Runs synchronously (blocks until all events are sent).
    """
    for event in events:
        print("[SCENARIO EVENT]", event)
        send_log(event)
        time.sleep(delay)


def run_scenario_async(
    events: list[dict[str, Any]], delay: float = SCENARIO_STEP_DELAY_SECONDS
) -> threading.Thread:
    """
    Replay a scenario in a background daemon thread.

    Returns the thread so the caller can join if needed.
    """
    t = threading.Thread(
        target=run_scenario,
        args=(events, delay),
        daemon=True,
        name="scenario-replay",
    )
    t.start()
    return t


# ---------------------------------------------------------------------------
# Legacy entry-point (kept for compatibility with the problem specification)
# ---------------------------------------------------------------------------

def run() -> None:  # pragma: no cover
    """Blocking run loop – kept for direct ``python simulator/engine.py`` usage."""
    start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop()


if __name__ == "__main__":  # pragma: no cover
    run()
