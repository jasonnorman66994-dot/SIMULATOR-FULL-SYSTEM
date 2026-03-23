"""
Integration tests for the FastAPI backend HTTP endpoints.

Uses FastAPI's built-in TestClient (backed by httpx) so no real server is
started.  Each test class resets shared state before running so tests are
fully independent and can be run in any order.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from backend import state
from backend.main import app
from compliance import logger as audit
from simulator import engine as sim_engine

client = TestClient(app, raise_server_exceptions=True)


@pytest.fixture(autouse=True)
def clean():
    """Reset all shared state before every test."""
    sim_engine.stop()
    state.reset()
    audit.reset_log()
    yield
    sim_engine.stop()
    state.reset()
    audit.reset_log()


# ---------------------------------------------------------------------------
# GET /alerts
# ---------------------------------------------------------------------------

class TestGetAlerts:
    def test_returns_empty_list_initially(self):
        res = client.get("/alerts")
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_stored_alerts(self):
        state.add_alert({"id": 1, "severity": "high", "type": "phishing_click"})
        res = client.get("/alerts")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["type"] == "phishing_click"

    def test_limit_parameter(self):
        for i in range(10):
            state.add_alert({"id": i, "severity": "low"})
        res = client.get("/alerts?limit=3")
        assert res.status_code == 200
        assert len(res.json()) == 3

    def test_response_is_json_array(self):
        res = client.get("/alerts")
        assert isinstance(res.json(), list)


# ---------------------------------------------------------------------------
# GET /stats
# ---------------------------------------------------------------------------

class TestGetStats:
    def test_returns_expected_keys(self):
        res = client.get("/stats")
        assert res.status_code == 200
        data = res.json()
        for key in ("attacks_per_min", "ai_actions", "threats_blocked", "compliance_score"):
            assert key in data, f"Missing key: {key}"

    def test_compliance_score_present(self):
        res = client.get("/stats")
        assert "compliance_score" in res.json()

    def test_initial_counts_are_zero(self):
        res = client.get("/stats")
        data = res.json()
        assert data["attacks_per_min"] == 0
        assert data["ai_actions"] == 0
        assert data["threats_blocked"] == 0


# ---------------------------------------------------------------------------
# GET /compliance/log
# ---------------------------------------------------------------------------

class TestGetComplianceLog:
    def test_returns_empty_list_initially(self):
        res = client.get("/compliance/log")
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_logged_actions(self):
        audit.log_action("block_ip", {"target": "1.2.3.4"})
        res = client.get("/compliance/log")
        data = res.json()
        assert len(data) == 1
        assert data[0]["action"] == "block_ip"


# ---------------------------------------------------------------------------
# POST /simulate/start  &  POST /simulate/stop
# ---------------------------------------------------------------------------

class TestSimulateStartStop:
    def test_start_returns_started_status(self):
        res = client.post("/simulate/start")
        assert res.status_code == 200
        assert res.json()["status"] == "simulation started"

    def test_start_twice_returns_already_running(self):
        client.post("/simulate/start")
        res = client.post("/simulate/start")
        assert res.json()["status"] == "already running"

    def test_stop_after_start_returns_stopped(self):
        client.post("/simulate/start")
        res = client.post("/simulate/stop")
        assert res.status_code == 200
        assert res.json()["status"] == "simulation stopped"

    def test_stop_when_not_running_returns_not_running(self):
        res = client.post("/simulate/stop")
        assert res.json()["status"] == "not running"


# ---------------------------------------------------------------------------
# GET /simulate/status
# ---------------------------------------------------------------------------

class TestSimulateStatus:
    def test_status_false_initially(self):
        res = client.get("/simulate/status")
        assert res.status_code == 200
        assert res.json()["running"] is False

    def test_status_true_after_start(self):
        client.post("/simulate/start")
        res = client.get("/simulate/status")
        assert res.json()["running"] is True

    def test_status_false_after_stop(self):
        client.post("/simulate/start")
        client.post("/simulate/stop")
        res = client.get("/simulate/status")
        assert res.json()["running"] is False


# ---------------------------------------------------------------------------
# POST /simulate/reset
# ---------------------------------------------------------------------------

class TestSimulateReset:
    def test_reset_clears_alerts(self):
        state.add_alert({"severity": "high"})
        client.post("/simulate/reset")
        assert client.get("/alerts").json() == []

    def test_reset_clears_compliance_log(self):
        audit.log_action("x", {})
        client.post("/simulate/reset")
        assert client.get("/compliance/log").json() == []

    def test_reset_returns_success_status(self):
        res = client.post("/simulate/reset")
        assert res.status_code == 200
        assert res.json()["status"] == "reset complete"

    def test_reset_stops_running_simulation(self):
        client.post("/simulate/start")
        client.post("/simulate/reset")
        assert client.get("/simulate/status").json()["running"] is False


# ---------------------------------------------------------------------------
# POST /simulate/scenario/{name}
# ---------------------------------------------------------------------------

class TestSimulateScenario:
    def test_known_scenario_returns_200(self):
        for name in ("phishing", "credential_stuffing", "impossible_travel", "data_exfiltration"):
            res = client.post(f"/simulate/scenario/{name}")
            assert res.status_code == 200, f"Expected 200 for scenario '{name}'"

    def test_known_scenario_returns_event_count(self):
        res = client.post("/simulate/scenario/phishing")
        data = res.json()
        assert "event_count" in data
        assert data["event_count"] > 0

    def test_known_scenario_status_field(self):
        res = client.post("/simulate/scenario/phishing")
        assert "phishing" in res.json()["status"]

    def test_unknown_scenario_returns_404(self):
        res = client.post("/simulate/scenario/totally_unknown")
        assert res.status_code == 404

    def test_unknown_scenario_returns_available_list(self):
        res = client.post("/simulate/scenario/bad_name")
        data = res.json()
        assert "available" in data
        assert "phishing" in data["available"]


# ---------------------------------------------------------------------------
# POST /ai/analyze
# ---------------------------------------------------------------------------

class TestAIAnalyze:
    def test_returns_200_for_known_event(self):
        res = client.post(
            "/ai/analyze",
            json={"event": {"type": "phishing_click", "user": "alice", "ip": "1.2.3.4"}},
        )
        assert res.status_code == 200

    def test_response_contains_detection_and_analysis(self):
        res = client.post(
            "/ai/analyze",
            json={"event": {"type": "credential_stuffing", "user": "bob"}},
        )
        data = res.json()
        assert "detection" in data
        assert "analysis" in data

    def test_detection_fires_alert_for_known_type(self):
        res = client.post(
            "/ai/analyze",
            json={"event": {"type": "data_exfiltration"}},
        )
        assert res.json()["detection"]["alert"] is True

    def test_analysis_contains_summary(self):
        res = client.post(
            "/ai/analyze",
            json={"event": {"type": "impossible_travel", "user": "charlie"}},
        )
        assert res.json()["analysis"]["summary"]

    def test_analysis_contains_recommended_actions(self):
        res = client.post(
            "/ai/analyze",
            json={"event": {"type": "phishing_click"}},
        )
        actions = res.json()["analysis"]["recommended_actions"]
        assert isinstance(actions, list)
        assert len(actions) > 0

    def test_unknown_event_type_returns_no_alert(self):
        res = client.post(
            "/ai/analyze",
            json={"event": {"type": "completely_unknown"}},
        )
        assert res.json()["detection"]["alert"] is False

    def test_top_level_event_body_fallback(self):
        """Body without 'event' wrapper is treated as the event itself."""
        res = client.post(
            "/ai/analyze",
            json={"type": "suspicious_login", "ip": "5.5.5.5"},
        )
        assert res.status_code == 200
