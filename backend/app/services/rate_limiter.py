from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Deque

from app.core.config import settings


class RateLimiter:
    """
    Per-endpoint sliding window rate limiter.
    """

    def __init__(self):
        self._events: dict[str, Deque[datetime]] = defaultdict(deque)

    def is_allowed(self, endpoint_id: str) -> bool:
        now = datetime.now(timezone.utc)
        window = settings.RATE_LIMIT_WINDOW_SECONDS
        limit = settings.MAX_EVENTS_PER_MINUTE

        queue = self._events[endpoint_id]

        # Remove expired timestamps
        while queue and (now - queue[0]).total_seconds() > window:
            queue.popleft()

        if len(queue) >= limit:
            return False

        queue.append(now)
        return True

    def reset(self) -> None:
        """
        Test isolation hook.
        Clears in-memory rate tracking.
        """
        self._events.clear()


rate_limiter = RateLimiter()
