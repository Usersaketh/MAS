from app.services.security import RateLimitService


def test_rate_limiter_blocks_after_limit():
    limiter = RateLimitService(requests_per_window=2, window_seconds=60)

    assert limiter.allow("api-key-1") is True
    assert limiter.allow("api-key-1") is True
    assert limiter.allow("api-key-1") is False
