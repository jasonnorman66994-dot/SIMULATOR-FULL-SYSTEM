"""Tests for the compliance logger."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time
import pytest
from compliance.logger import log_action, get_log, compliance_score, reset_log


@pytest.fixture(autouse=True)
def clean_log():
    reset_log()
    yield
    reset_log()


class TestLogAction:
    def test_returns_entry_with_timestamp(self):
        entry = log_action("block_ip", {"target": "1.2.3.4"})
        assert "timestamp" in entry
        assert abs(entry["timestamp"] - time.time()) < 2

    def test_entry_stored_in_log(self):
        log_action("test_action", {"detail": "x"})
        log = get_log()
        assert len(log) == 1
        assert log[0]["action"] == "test_action"

    def test_multiple_entries_appended(self):
        for i in range(5):
            log_action(f"action_{i}", {})
        assert len(get_log()) == 5

    def test_get_log_returns_snapshot(self):
        log_action("a", {})
        snap1 = get_log()
        log_action("b", {})
        snap2 = get_log()
        assert len(snap1) == 1
        assert len(snap2) == 2


class TestComplianceScore:
    def test_score_starts_at_50_with_no_actions(self):
        assert compliance_score() == 50.0

    def test_score_increases_with_actions(self):
        log_action("x", {})
        assert compliance_score() > 50.0

    def test_score_capped_at_100(self):
        for _ in range(100):
            log_action("x", {})
        assert compliance_score() <= 100.0


class TestResetLog:
    def test_clears_entries(self):
        log_action("x", {})
        reset_log()
        assert get_log() == []

    def test_score_returns_to_50_after_reset(self):
        log_action("x", {})
        reset_log()
        assert compliance_score() == 50.0
