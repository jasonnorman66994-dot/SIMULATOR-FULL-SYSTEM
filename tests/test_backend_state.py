"""Unit tests for the backend.state module."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from backend import state


@pytest.fixture(autouse=True)
def clean_state():
    state.reset()
    yield
    state.reset()


class TestAddAlert:
    def test_alert_is_stored(self):
        state.add_alert({"id": 1, "severity": "low"})
        alerts = state.get_alerts()
        assert len(alerts) == 1
        assert alerts[0]["id"] == 1

    def test_high_severity_increments_threats_blocked(self):
        state.add_alert({"severity": "high"})
        assert state.get_stats()["threats_blocked"] == 1

    def test_critical_severity_increments_threats_blocked(self):
        state.add_alert({"severity": "critical"})
        assert state.get_stats()["threats_blocked"] == 1

    def test_low_severity_does_not_increment_threats_blocked(self):
        state.add_alert({"severity": "low"})
        assert state.get_stats()["threats_blocked"] == 0

    def test_medium_severity_does_not_increment_threats_blocked(self):
        state.add_alert({"severity": "medium"})
        assert state.get_stats()["threats_blocked"] == 0

    def test_add_alert_increments_attacks_per_min(self):
        state.add_alert({"severity": "low"})
        state.add_alert({"severity": "low"})
        assert state.get_stats()["attacks_per_min"] == 2

    def test_max_alerts_cap_enforced(self):
        for i in range(state.MAX_ALERTS + 10):
            state.add_alert({"id": i, "severity": "low"})
        assert len(state.get_alerts(limit=state.MAX_ALERTS + 10)) <= state.MAX_ALERTS

    def test_oldest_alert_dropped_when_over_cap(self):
        for i in range(state.MAX_ALERTS + 1):
            state.add_alert({"id": i, "severity": "low"})
        ids = [a["id"] for a in state.get_alerts(limit=state.MAX_ALERTS + 10)]
        assert 0 not in ids  # oldest entry should have been evicted


class TestGetAlerts:
    def test_returns_empty_list_initially(self):
        assert state.get_alerts() == []

    def test_limit_parameter_respected(self):
        for i in range(10):
            state.add_alert({"id": i, "severity": "low"})
        assert len(state.get_alerts(limit=3)) == 3

    def test_returns_snapshot_not_reference(self):
        state.add_alert({"id": 1, "severity": "low"})
        snap = state.get_alerts()
        state.add_alert({"id": 2, "severity": "low"})
        assert len(snap) == 1  # snapshot unchanged


class TestIncrementAiActions:
    def test_starts_at_zero(self):
        assert state.get_stats()["ai_actions"] == 0

    def test_increments_by_one(self):
        state.increment_ai_actions()
        assert state.get_stats()["ai_actions"] == 1

    def test_multiple_increments(self):
        for _ in range(5):
            state.increment_ai_actions()
        assert state.get_stats()["ai_actions"] == 5


class TestGetStats:
    def test_returns_all_keys(self):
        s = state.get_stats()
        assert "attacks_per_min" in s
        assert "ai_actions" in s
        assert "threats_blocked" in s

    def test_returns_copy_not_reference(self):
        s = state.get_stats()
        s["attacks_per_min"] = 9999
        assert state.get_stats()["attacks_per_min"] != 9999


class TestReset:
    def test_clears_alerts(self):
        state.add_alert({"severity": "low"})
        state.reset()
        assert state.get_alerts() == []

    def test_resets_all_stats_to_zero(self):
        state.add_alert({"severity": "critical"})
        state.increment_ai_actions()
        state.reset()
        s = state.get_stats()
        assert s["attacks_per_min"] == 0
        assert s["ai_actions"] == 0
        assert s["threats_blocked"] == 0
