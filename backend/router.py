"""
FastAPI router – all HTTP and WebSocket endpoints.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from ai_soc import agent as ai_agent
from backend import state
from compliance import logger as audit
from detection import engine as detection_engine
from ingestion.producer import get_event
from response.actions import execute_action
from simulator import engine as sim_engine
from simulator.scenarios.credential_stuffing import credential_stuffing_scenario
from simulator.scenarios.data_exfiltration import data_exfiltration_scenario
from simulator.scenarios.impossible_travel import impossible_travel_scenario
from simulator.scenarios.phishing import phishing_scenario

router = APIRouter()


# ---------------------------------------------------------------------------
# Background event-processing task
# ---------------------------------------------------------------------------

async def _process_events() -> None:
    """Drain the ingestion queue and push enriched alerts to connected clients."""
    while True:
        event = get_event()
        if event:
            # Detection
            detection_result = detection_engine.detect(event)
            if detection_result.get("alert"):
                # AI analysis
                analysis = ai_agent.analyze(detection_result)
                state.increment_ai_actions()

                # Auto-response
                recommended = detection_result.get("recommended_action", "")
                action_result: dict[str, Any] = {}
                if recommended:
                    action_result = execute_action(recommended, event)

                # Build enriched alert
                alert: dict[str, Any] = {
                    "id": int(time.time() * 1000),
                    "type": event.get("type", event.get("event", "unknown")),
                    "user": event.get("user", "unknown"),
                    "ip": event.get("ip", "unknown"),
                    "severity": detection_result.get("severity", "medium"),
                    "description": detection_result.get("description", ""),
                    "attack_chain": analysis.get("attack_chain", ""),
                    "risk": analysis.get("risk", ""),
                    "ai_summary": analysis.get("summary", ""),
                    "mitre": analysis.get("mitre_technique", ""),
                    "action_taken": action_result.get("action", ""),
                    "action_status": action_result.get("status", ""),
                    "timestamp": event.get("timestamp", time.time()),
                }
                state.add_alert(alert)

                # Push to all WebSocket clients
                message = json.dumps({"type": "alert", "data": alert})
                for ws in state.get_connections():
                    try:
                        await ws.send_text(message)
                    except Exception:
                        state.unregister_ws(ws)

        await asyncio.sleep(0.1)


# ---------------------------------------------------------------------------
# HTTP endpoints
# ---------------------------------------------------------------------------

@router.get("/alerts")
def get_alerts(limit: int = 50) -> JSONResponse:
    """Return the most recent *limit* enriched alerts."""
    return JSONResponse(content=state.get_alerts(limit))


@router.get("/stats")
def get_stats() -> JSONResponse:
    """Return real-time counters."""
    data = state.get_stats()
    data["compliance_score"] = audit.compliance_score()
    return JSONResponse(content=data)


@router.get("/compliance/log")
def get_compliance_log() -> JSONResponse:
    """Return the full audit / compliance log."""
    return JSONResponse(content=audit.get_log())


@router.post("/simulate/start")
def start_simulation() -> JSONResponse:
    """Start the random attack simulator background thread."""
    started = sim_engine.start()
    return JSONResponse(
        content={"status": "simulation started" if started else "already running"}
    )


@router.post("/simulate/stop")
def stop_simulation() -> JSONResponse:
    """Stop the random attack simulator."""
    stopped = sim_engine.stop()
    return JSONResponse(
        content={"status": "simulation stopped" if stopped else "not running"}
    )


@router.get("/simulate/status")
def simulation_status() -> JSONResponse:
    """Return whether the simulator is currently running."""
    return JSONResponse(content={"running": sim_engine.is_running()})


@router.post("/simulate/reset")
def reset_demo() -> JSONResponse:
    """Clear all alerts, stats, and compliance log (demo reset)."""
    sim_engine.stop()
    state.reset()
    audit.reset_log()
    return JSONResponse(content={"status": "reset complete"})


@router.post("/simulate/scenario/{name}")
def run_scenario(name: str) -> JSONResponse:
    """
    Trigger a named scenario.

    Available: ``phishing``, ``credential_stuffing``, ``impossible_travel``,
    ``data_exfiltration``.
    """
    scenarios = {
        "phishing": phishing_scenario,
        "credential_stuffing": credential_stuffing_scenario,
        "impossible_travel": impossible_travel_scenario,
        "data_exfiltration": data_exfiltration_scenario,
    }
    fn = scenarios.get(name)
    if fn is None:
        return JSONResponse(
            status_code=404,
            content={"error": f"Unknown scenario '{name}'", "available": list(scenarios)},
        )
    events = fn()
    sim_engine.run_scenario_async(events)
    return JSONResponse(content={"status": f"scenario '{name}' started", "event_count": len(events)})


@router.post("/ai/analyze")
async def ai_analyze(body: dict[str, Any]) -> JSONResponse:
    """
    Ask the AI SOC agent to analyse a custom event payload.

    Body: ``{ "event": { ... } }``
    """
    event = body.get("event", body)
    detection_result = detection_engine.detect(event)
    analysis = ai_agent.analyze(detection_result)
    return JSONResponse(content={"detection": detection_result, "analysis": analysis})


# ---------------------------------------------------------------------------
# WebSocket
# ---------------------------------------------------------------------------

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Real-time push channel – streams enriched alerts as JSON."""
    await websocket.accept()
    state.register_ws(websocket)
    try:
        # Send current alerts on connect
        for alert in state.get_alerts():
            await websocket.send_text(json.dumps({"type": "alert", "data": alert}))
        # Keep connection alive
        while True:
            await websocket.receive_text()  # wait for client ping / close
    except WebSocketDisconnect:
        pass
    finally:
        state.unregister_ws(websocket)
