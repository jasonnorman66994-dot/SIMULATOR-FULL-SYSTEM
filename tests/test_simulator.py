"""Tests for the simulator engine and scenario modules."""

import time
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from simulator.engine import generate_attack, start, stop, is_running
from simulator.scenarios.phishing import phishing_scenario
from simulator.scenarios.credential_stuffing import credential_stuffing_scenario
from simulator.scenarios.impossible_travel import impossible_travel_scenario
from simulator.scenarios.data_exfiltration import data_exfiltration_scenario


class TestGenerateAttack:
    def test_returns_dict_with_required_keys(self):
        event = generate_attack()
        for key in ("type", "user", "ip", "severity", "timestamp"):
            assert key in event, f"Missing key: {key}"

    def test_type_is_valid(self):
        valid = {"phishing_click", "credential_stuffing", "impossible_travel", "data_exfiltration"}
        for _ in range(20):
            event = generate_attack()
            assert event["type"] in valid

    def test_severity_is_valid(self):
        valid = {"low", "medium", "high", "critical"}
        for _ in range(20):
            event = generate_attack()
            assert event["severity"] in valid

    def test_timestamp_is_recent(self):
        event = generate_attack()
        assert abs(event["timestamp"] - time.time()) < 5


class TestSimulatorControl:
    def teardown_method(self, _):
        stop()

    def test_start_returns_true_when_not_running(self):
        assert start() is True

    def test_start_returns_false_when_already_running(self):
        start()
        assert start() is False

    def test_stop_returns_true_when_running(self):
        start()
        assert stop() is True

    def test_stop_returns_false_when_not_running(self):
        assert stop() is False

    def test_is_running_reflects_state(self):
        assert is_running() is False
        start()
        assert is_running() is True
        stop()
        assert is_running() is False


class TestPhishingScenario:
    def test_returns_list_of_four_events(self):
        events = phishing_scenario()
        assert len(events) == 4

    def test_events_have_correct_types(self):
        expected = ["email_delivered", "link_clicked", "credential_entered", "suspicious_login"]
        for event, exp in zip(phishing_scenario(), expected):
            assert event["type"] == exp

    def test_custom_user_and_ip(self):
        events = phishing_scenario(user="testuser", attacker_ip="1.2.3.4")
        for e in events:
            assert e["user"] == "testuser"
            assert e["ip"] == "1.2.3.4"


class TestCredentialStuffingScenario:
    def test_returns_nonempty_list(self):
        events = credential_stuffing_scenario()
        assert len(events) > 0

    def test_all_events_are_critical(self):
        events = credential_stuffing_scenario()
        for e in events:
            assert e["severity"] == "critical"

    def test_custom_ip(self):
        events = credential_stuffing_scenario(attacker_ip="5.5.5.5")
        for e in events:
            assert e["ip"] == "5.5.5.5"


class TestImpossibleTravelScenario:
    def test_returns_two_events(self):
        events = impossible_travel_scenario()
        assert len(events) == 2

    def test_second_event_is_higher_severity(self):
        events = impossible_travel_scenario()
        assert events[1]["severity"] == "high"


class TestDataExfiltrationScenario:
    def test_returns_two_events(self):
        events = data_exfiltration_scenario()
        assert len(events) == 2

    def test_last_event_is_critical(self):
        events = data_exfiltration_scenario()
        assert events[-1]["severity"] == "critical"
