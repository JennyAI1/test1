import time
from collections import defaultdict

from fastapi import HTTPException, status

RATE_BUCKETS: dict[str, list[float]] = defaultdict(list)


def enforce_rate_limit(key: str, max_requests: int, window_seconds: int) -> None:
    now = time.time()
    window_start = now - window_seconds
    bucket = [ts for ts in RATE_BUCKETS[key] if ts >= window_start]

    if len(bucket) >= max_requests:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again later.",
        )

    bucket.append(now)
    RATE_BUCKETS[key] = bucket
