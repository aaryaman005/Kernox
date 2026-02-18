from typing import Set


class EventGuard:
    """
    In-memory replay protection.
    Reset before every test via fixture.
    """

    def __init__(self):
        self._seen: Set[str] = set()

    def is_duplicate(self, event_id: str) -> bool:
        return event_id in self._seen

    def record(self, event_id: str) -> None:
        self._seen.add(event_id)

    def reset(self) -> None:
        self._seen.clear()


event_guard = EventGuard()
