"""
LUMEN Sprint 10 — Rate Limiting (Block 7)

Per-IP / per-path-prefix sliding-window rate limit middleware.

Why a custom middleware?
  - slowapi's @limit decorator must be applied per-route. Lumen has 80+
    endpoints; touching each is risky and noisy.
  - We need uniform protection on auth / kyc / contracts / payments /
    withdrawals path families without rewriting handlers.

Storage: in-process dict (deque) per (ip, prefix). Reset on restart — good
enough for a preview pod. For production add a redis backend (see TODO).

Limits (per minute, per IP)
  /api/auth/*          30
  /api/kyc/*           60
  /api/contracts/*     60
  /api/payments/*      30
  /api/payment-proofs/ 30
  /api/withdrawals/*   30
  /api/investor/withdrawals*   20    # outflow endpoints — extra caution
"""
from __future__ import annotations

import logging
import time
from collections import deque
from typing import Deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("lumen.ratelimit")

# (path_prefix, per_minute_limit). First match wins so order matters.
RULES: list[tuple[str, int]] = [
    ("/api/investor/withdrawals", 20),
    ("/api/admin/withdrawals", 60),
    ("/api/withdrawals", 30),
    ("/api/auth/", 30),
    ("/api/investor/kyc", 60),
    ("/api/admin/kyc", 60),
    ("/api/kyc/", 60),
    ("/api/contracts/", 60),
    ("/api/investor/contracts", 60),
    ("/api/admin/contracts", 60),
    ("/api/payment-proofs/", 30),
    ("/api/investor/payments", 30),
    ("/api/admin/payments", 60),
    ("/api/payments/", 30),
]

WINDOW_SECONDS = 60

# (ip, prefix) -> deque of timestamps
_BUCKETS: dict[tuple[str, str], Deque[float]] = {}


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _match_rule(path: str) -> tuple[str, int] | None:
    for prefix, limit in RULES:
        if path.startswith(prefix):
            return prefix, limit
    return None


class LumenRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only HTTP API routes are subject to rate limiting.
        path = request.url.path
        rule = _match_rule(path)
        if rule is None:
            return await call_next(request)
        prefix, limit = rule
        ip = _client_ip(request)
        key = (ip, prefix)
        now = time.monotonic()
        bucket = _BUCKETS.setdefault(key, deque())
        # Drop timestamps older than window
        while bucket and (now - bucket[0]) > WINDOW_SECONDS:
            bucket.popleft()
        if len(bucket) >= limit:
            retry = max(1, int(WINDOW_SECONDS - (now - bucket[0])))
            logger.warning(
                "RATE-LIMIT 429: ip=%s prefix=%s count=%s/%s retry_in=%ss",
                ip, prefix, len(bucket), limit, retry,
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Перевищено ліміт запитів. Зачекайте і спробуйте знову.",
                    "code": "rate_limit_exceeded",
                    "limit": limit,
                    "window_seconds": WINDOW_SECONDS,
                    "retry_after_seconds": retry,
                },
                headers={"Retry-After": str(retry)},
            )
        bucket.append(now)
        return await call_next(request)


__all__ = ["LumenRateLimitMiddleware", "RULES", "WINDOW_SECONDS"]
