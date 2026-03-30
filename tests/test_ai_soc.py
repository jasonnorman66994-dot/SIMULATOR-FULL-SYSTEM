"""Tests for the AI SOC agent."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from ai_soc.agent import analyze


class TestAnalyze:
    def _detection(self, attack_type):
        return {
            "alert": True,
            "rule_matched": attack_type,
            "recommended_action": "block_ip",
            "severity": "high",
            "event": {"type": attack_type, "user": "alice", "ip": "1.2.3.4"},
        }

    def test_no_alert_returns_no_threat_summary(self):
        result = analyze({"alert": False})
        assert "no threat" in result["summary"].lower()

    def test_known_type_returns_summary(self):
        result = analyze(self._detection("phishing_click"))
        assert result["summary"]
        assert len(result["summary"]) > 10

    def test_known_type_returns_attack_chain(self):
        result = analyze(self._detection("credential_stuffing"))
        assert result["attack_chain"]

    def test_known_type_returns_recommended_actions(self):
        result = analyze(self._detection("data_exfiltration"))
        assert isinstance(result["recommended_actions"], list)
        assert len(result["recommended_actions"]) > 0

    def test_known_type_returns_mitre_technique(self):
        result = analyze(self._detection("impossible_travel"))
        assert result["mitre_technique"]

    def test_unknown_type_returns_default_analysis(self):
        result = analyze(
            {
                "alert": True,
                "rule_matched": "unknown_weird_attack",
                "event": {"type": "unknown_weird_attack"},
            }
        )
        assert result["summary"]
        assert "flag_account" in result["recommended_actions"]

    def test_all_known_attack_types_have_analysis(self):
        known = [
            "phishing_click",
            "credential_stuffing",
            "impossible_travel",
            "data_exfiltration",
            "email_delivered",
            "link_clicked",
            "credential_entered",
            "suspicious_login",
        ]
        for t in known:
            result = analyze(self._detection(t))
            assert result["summary"], f"No summary for {t}"
