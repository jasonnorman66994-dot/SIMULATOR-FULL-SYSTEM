"""
Event pipeline – ingestion layer.

Sends events to the downstream processing queue.  When a real Kafka cluster
is configured via KAFKA_BOOTSTRAP_SERVERS the events are published to the
configured topic; otherwise they flow through an in-process thread-safe queue
so the whole system runs stand-alone without any external dependencies.
"""

from __future__ import annotations

import json
import queue
import threading
from typing import Any

from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC

# ---------------------------------------------------------------------------
# In-process fallback queue (used when Kafka is not configured)
# ---------------------------------------------------------------------------
_event_queue: queue.Queue[dict] = queue.Queue()
_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Optional Kafka producer (lazy-initialised)
# ---------------------------------------------------------------------------
_kafka_producer = None


def _get_kafka_producer():
    """Return a cached KafkaProducer or None if Kafka is unavailable."""
    global _kafka_producer  # noqa: PLW0603
    if _kafka_producer is not None:
        return _kafka_producer
    if not KAFKA_BOOTSTRAP_SERVERS:
        return None
    try:
        from kafka import KafkaProducer  # type: ignore[import]

        _kafka_producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        return _kafka_producer
    except Exception:  # pragma: no cover – Kafka optional
        return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def send_log(event: dict[str, Any]) -> None:
    """Publish *event* to the pipeline (Kafka or in-process queue)."""
    producer = _get_kafka_producer()
    if producer is not None:
        try:
            producer.send(KAFKA_TOPIC, event)
            return
        except Exception:  # pragma: no cover
            pass  # fall through to in-process queue

    _event_queue.put(event)


def get_event() -> dict[str, Any] | None:
    """Return the next event from the in-process queue, or *None* if empty."""
    try:
        return _event_queue.get_nowait()
    except queue.Empty:
        return None


def queue_size() -> int:
    """Return the approximate number of pending events in the in-process queue."""
    return _event_queue.qsize()
