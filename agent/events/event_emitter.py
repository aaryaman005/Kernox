"""
Kernox — Event Emitter

Formats security events as structured JSON and outputs them.
Phase 1: stdout output.
Future: HTTP POST to backend API.
"""

import json
import sys
import threading
from datetime import datetime, timezone

from agent.config import HOSTNAME, ENDPOINT_ID, EVENT_OUTPUT_MODE


class EventEmitter:
    """
    Thread-safe event formatter and emitter.

    Each event is enriched with standard metadata and output as
    a single-line JSON record.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._event_count = 0
        self._last_event_time: str | None = None

    def emit(self, event: dict) -> None:
        """
        Enrich and emit a security event.

        Args:
            event: Raw event dict with at minimum:
                - event_type: str
                - pid: int
                - ppid: int
        """
        enriched = self._enrich(event)
        self._output(enriched)

        with self._lock:
            self._event_count += 1
            self._last_event_time = enriched["timestamp"]

    @property
    def event_count(self) -> int:
        with self._lock:
            return self._event_count

    @property
    def last_event_time(self) -> str | None:
        with self._lock:
            return self._last_event_time

    # ── Internal ─────────────────────────────────────────────────

    def _enrich(self, event: dict) -> dict:
        """Add standard metadata fields to a raw event."""
        enriched = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hostname": HOSTNAME,
            "endpoint_id": ENDPOINT_ID,
        }
        enriched.update(event)
        return enriched

    def _output(self, event: dict) -> None:
        """Write event to configured output (stdout for now)."""
        line = json.dumps(event, default=str)

        if EVENT_OUTPUT_MODE == "stdout":
            with self._lock:
                sys.stdout.write(line + "\n")
                sys.stdout.flush()
        # Future: elif EVENT_OUTPUT_MODE == "http":
        #     requests.post(API_EVENTS_ENDPOINT, json=event)
