import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

class RateLimiter:
    """Allow at most 'max_calls' request per 'per_seconds' for each client IP."""

    def __init__(self, max_calls: int, per_seconds: int):
        self.max_calls = max_calls
        self.per_seconds = per_seconds
        self._calls= defaultdict(deque)
        self._lock = threading.Lock()

    def __call__(self, request: Request) -> None:
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()

        with self._lock:
            window = self._calls[client]
            while window and now - window[0] > self.per_seconds:
                window.popleft()
            if len(window) >= self.max_calls:
                raise HTTPException(
                    status_code=429,
                    detail="Too many request. Please slow down and try again shortly.",
                    headers={"Retry-After": str(self.per_seconds)},
                )
            window.append(now)