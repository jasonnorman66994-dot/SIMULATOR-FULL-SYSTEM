"""Tests for the ingestion producer (in-process queue fallback)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from ingestion import producer


@pytest.fixture(autouse=True)
def drain_queue():
    """Drain the in-process queue before and after every test."""
    while producer.get_event() is not None:
        pass
    yield
    while producer.get_event() is not None:
        pass


class TestSendLog:
    def test_send_then_get_returns_event(self):
        from ingestion.producer import send_log, get_event
        event = {"type": "test", "user": "alice"}
        send_log(event)
        received = get_event()
        assert received == event

    def test_get_on_empty_queue_returns_none(self):
        from ingestion.producer import get_event
        assert get_event() is None

    def test_fifo_order_preserved(self):
        from ingestion.producer import send_log, get_event
        events = [{"id": i} for i in range(5)]
        for e in events:
            send_log(e)
        received = [get_event() for _ in range(5)]
        assert received == events

    def test_queue_size_reflects_pending(self):
        from ingestion.producer import send_log, queue_size
        initial = queue_size()
        send_log({"type": "a"})
        send_log({"type": "b"})
        assert queue_size() >= initial + 2
