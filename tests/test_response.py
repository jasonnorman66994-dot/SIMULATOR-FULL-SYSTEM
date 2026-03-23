"""Tests for the response actions module."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from response.actions import block_ip, revoke_session, flag_account, isolate_device, execute_action, ACTION_MAP
from compliance import logger as audit


def setup_function():
    audit.reset_log()


class TestBlockIp:
    def test_returns_dict_with_action(self):
        result = block_ip("1.2.3.4", simulation_mode=True)
        assert result["action"] == "block_ip"

    def test_simulated_status(self):
        result = block_ip("1.2.3.4", simulation_mode=True)
        assert result["status"] == "simulated"
        assert result["simulated"] is True

    def test_target_is_ip(self):
        result = block_ip("9.9.9.9", simulation_mode=True)
        assert result["target"] == "9.9.9.9"

    def test_writes_to_audit_log(self):
        audit.reset_log()
        block_ip("8.8.8.8", simulation_mode=True)
        log = audit.get_log()
        assert len(log) == 1
        assert log[0]["action"] == "block_ip"


class TestRevokeSession:
    def test_returns_dict_with_action(self):
        result = revoke_session("alice", simulation_mode=True)
        assert result["action"] == "revoke_session"

    def test_target_is_user(self):
        result = revoke_session("bob", simulation_mode=True)
        assert result["target"] == "bob"


class TestFlagAccount:
    def test_returns_dict_with_action(self):
        result = flag_account("charlie", simulation_mode=True)
        assert result["action"] == "flag_account"


class TestIsolateDevice:
    def test_returns_dict_with_action(self):
        result = isolate_device("dave", simulation_mode=True)
        assert result["action"] == "isolate_device"


class TestExecuteAction:
    def test_dispatches_block_ip(self):
        event = {"type": "credential_stuffing", "user": "alice", "ip": "5.5.5.5"}
        result = execute_action("block_ip", event, simulation_mode=True)
        assert result["action"] == "block_ip"
        assert result["target"] == "5.5.5.5"

    def test_dispatches_revoke_session(self):
        event = {"type": "phishing_click", "user": "alice", "ip": "5.5.5.5"}
        result = execute_action("revoke_session", event, simulation_mode=True)
        assert result["action"] == "revoke_session"
        assert result["target"] == "alice"

    def test_unknown_action_returns_unknown_status(self):
        result = execute_action("nuke_everything", {}, simulation_mode=True)
        assert result["status"] == "unknown_action"

    def test_all_actions_in_map_are_callable(self):
        for name, fn in ACTION_MAP.items():
            assert callable(fn), f"{name} is not callable"
