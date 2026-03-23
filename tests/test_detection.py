"""Tests for the detection engine."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from detection.engine import detect, DETECTION_RULES


class TestDetect:
    def test_known_attack_fires_alert(self):
        for attack_type in DETECTION_RULES:
            event = {"type": attack_type, "user": "alice", "ip": "1.2.3.4"}
            result = detect(event)
            assert result["alert"] is True, f"Expected alert for {attack_type}"

    def test_unknown_type_does_not_fire_alert(self):
        result = detect({"type": "totally_unknown_type"})
        assert result["alert"] is False

    def test_result_contains_required_keys_on_alert(self):
        result = detect({"type": "phishing_click", "user": "alice", "ip": "1.2.3.4"})
        for key in ("rule_matched", "recommended_action", "severity", "event", "timestamp"):
            assert key in result

    def test_phishing_click_recommends_revoke_session(self):
        result = detect({"type": "phishing_click"})
        assert result["recommended_action"] == "revoke_session"

    def test_credential_stuffing_recommends_block_ip(self):
        result = detect({"type": "credential_stuffing"})
        assert result["recommended_action"] == "block_ip"

    def test_data_exfiltration_recommends_isolate_device(self):
        result = detect({"type": "data_exfiltration"})
        assert result["recommended_action"] == "isolate_device"

    def test_impossible_travel_recommends_flag_account(self):
        result = detect({"type": "impossible_travel"})
        assert result["recommended_action"] == "flag_account"

    def test_event_field_also_triggers_detection(self):
        """scenario sub-events use 'event' key instead of 'type'"""
        result = detect({"event": "link_clicked", "user": "bob"})
        assert result["alert"] is True

    def test_severity_is_overridden_by_rule(self):
        result = detect({"type": "credential_stuffing", "severity": "low"})
        assert result["severity"] == "critical"
