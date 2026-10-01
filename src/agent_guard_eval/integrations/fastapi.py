"""FastAPI integration for the numeric guard.

Requires the optional ``fastapi`` dependency.
"""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any

from ..exceptions import GuardInputError
from ..guard import NumericGuard

try:
    from fastapi import Request
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse, Response
except ImportError as exc:  # pragma: no cover - depends on optional dependency
    raise ImportError(
        "The FastAPI integration requires 'fastapi'. "
        "Install with: pip install 'agent-guard-eval[fastapi]'"
    ) from exc


def create_guard_dependency(
    guard: NumericGuard,
    text_field: str = "text",
) -> Callable[[Request], Awaitable[dict[str, Any]]]:
    """Create a FastAPI dependency that validates ``text_field`` of the JSON body."""

    async def dependency(request: Request) -> dict[str, Any]:
        payload = await request.json()
        text = payload.get(text_field, "") if isinstance(payload, dict) else ""
        result = guard.validate(str(text))
        request.state.guard_result = result
        return result.to_dict()

    return dependency


class NumericGuardMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that validates JSON bodies and optionally blocks violations."""

    def __init__(
        self,
        app: Any,
        guard: NumericGuard,
        text_field: str = "text",
        block_on_violation: bool = True,
    ) -> None:
        super().__init__(app)
        self.guard = guard
        self.text_field = text_field
        self.block_on_violation = block_on_violation

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        content_type = request.headers.get("content-type", "")
        is_json = "application/json" in content_type
        if request.method in ("POST", "PUT", "PATCH") and is_json:
            try:
                body = await request.body()
                payload = json.loads(body or b"{}")
                text = payload.get(self.text_field) if isinstance(payload, dict) else None
                if isinstance(text, str):
                    result = self.guard.validate(text)
                    request.state.guard_result = result
                    if not result.is_valid and self.block_on_violation:
                        return JSONResponse(status_code=422, content=result.to_dict())
            except (json.JSONDecodeError, ValueError, GuardInputError):
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid JSON payload or input text"},
                )
        return await call_next(request)
