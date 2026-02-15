from typing import Set


class EventGuard:
    """
    In-memory replay protection guard.
    Will be replaced with DB uniqueness in Phase 2.
    """

    def __init__(self):
        self._seen_event_ids: Set[str] = set()

    def is_duplicate(self, event_id: str) -> bool:
        return event_id in self._seen_event_ids

    def record(self, event_id: str):
        self._seen_event_ids.add(event_id)


# Global instance
event_guard = EventGuard()
