"""In-memory sliding-window rate limiting for authentication endpoints.

Deliberately process-local: DualWell runs as a single uvicorn process, so a
module-level store is sufficient. If the API is ever sharded behind a load
balancer, swap this for a shared store (e.g. Redis) with the same interface.
"""

import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

from app.config import settings


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._events: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def retry_after(self, key: str, limit: int, window_seconds: int) -> Optional[float]:
        """Seconds until the key may retry, or None when the key is allowed."""
        cutoff = time.monotonic() - window_seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) < limit:
                return None
            return max(events[0] + window_seconds - time.monotonic(), 0.5)

    def record(self, key: str) -> None:
        with self._lock:
            self._events[key].append(time.monotonic())

    def reset(self, key: str) -> None:
        with self._lock:
            self._events.pop(key, None)


login_limiter = SlidingWindowLimiter()


def login_block_reason(email_key: str, ip_key: str) -> Optional[int]:
    """Returns Retry-After seconds when either key is throttled, else None."""
    limit = settings.LOGIN_RATE_LIMIT_ATTEMPTS
    window = settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS
    # The per-IP cap is deliberately looser: many legitimate users can share a
    # campus NAT, while a single account should never see this many failures.
    for key, key_limit in ((email_key, limit), (ip_key, limit * 5)):
        retry = login_limiter.retry_after(key, key_limit, window)
        if retry is not None:
            return int(retry) + 1
    return None


def record_login_failure(email_key: str, ip_key: str) -> None:
    login_limiter.record(email_key)
    login_limiter.record(ip_key)


def clear_login_failures(email_key: str, ip_key: str) -> None:
    login_limiter.reset(email_key)
    login_limiter.reset(ip_key)