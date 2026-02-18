import pytest
from app.services.event_guard import event_guard
from app.services.rate_limiter import rate_limiter


@pytest.fixture(autouse=True)
def reset_state():
    event_guard.reset()
    rate_limiter.reset()
