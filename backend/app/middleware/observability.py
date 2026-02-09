"""Middleware for RED metrics and trace propagation."""

from __future__ import annotations

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.observability import classify_domain, ensure_trace_id, metrics_store


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        trace_id_header = request.headers.get("x-trace-id") or request.headers.get("traceparent")
        trace_id = ensure_trace_id(trace_id_header)
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        domain = classify_domain(request.url.path)
        metrics_store.record_request(domain, request.method, response.status_code, duration_ms)
        response.headers["X-Trace-Id"] = trace_id
        return response
