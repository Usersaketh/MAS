from __future__ import annotations

from collections import deque
from threading import Lock
from time import monotonic

from fastapi import Header, HTTPException, Request, status

from app.core.config import settings


class RateLimitService:
    def __init__(self, requests_per_window: int, window_seconds: int = 60) -> None:
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = {}
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        now = monotonic()
        with self._lock:
            bucket = self._requests.setdefault(key, deque())
            while bucket and now - bucket[0] >= self.window_seconds:
                bucket.popleft()

            if len(bucket) >= self.requests_per_window:
                return False

            bucket.append(now)
            return True


rate_limiter = RateLimitService(settings.rate_limit_requests_per_minute, settings.rate_limit_window_seconds)


def enforce_request_security(
    request: Request,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> str:
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )

    client_host = request.client.host if request.client else "unknown"
    client_id = f"{x_api_key}:{client_host}"
    if not rate_limiter.allow(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
        )

    return x_api_key
