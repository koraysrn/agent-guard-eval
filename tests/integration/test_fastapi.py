"""Integration tests for the FastAPI adapter."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi import Depends, FastAPI
from starlette.testclient import TestClient

from agent_guard_eval import NumericGuard
from agent_guard_eval.integrations.fastapi import (
    NumericGuardMiddleware,
    create_guard_dependency,
)


def test_dependency_endpoint() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    app = FastAPI()

    @app.post("/check")
    async def check(result: dict = Depends(create_guard_dependency(guard))) -> dict:
        return result

    client = TestClient(app)
    response = client.post("/check", json={"text": "Sharpe: 1.5"})
    assert response.status_code == 200
    assert response.json()["is_valid"] is True


def test_middleware_blocks_violation() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    app = FastAPI()
    app.add_middleware(NumericGuardMiddleware, guard=guard)

    @app.post("/echo")
    async def echo(payload: dict) -> dict:
        return payload

    client = TestClient(app)
    response = client.post("/echo", json={"text": "Sharpe: 1.9"})
    assert response.status_code == 422
    assert response.json()["is_valid"] is False


def test_middleware_allows_valid() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    app = FastAPI()
    app.add_middleware(NumericGuardMiddleware, guard=guard)

    @app.post("/echo")
    async def echo(payload: dict) -> dict:
        return payload

    client = TestClient(app)
    response = client.post("/echo", json={"text": "Sharpe: 1.5"})
    assert response.status_code == 200
    assert response.json()["text"] == "Sharpe: 1.5"


def test_middleware_rejects_bad_json() -> None:
    guard = NumericGuard({"Sharpe": 1.5})
    app = FastAPI()
    app.add_middleware(NumericGuardMiddleware, guard=guard)

    @app.post("/echo")
    async def echo(payload: dict) -> dict:
        return payload

    client = TestClient(app)
    response = client.post(
        "/echo", content=b"{not json", headers={"content-type": "application/json"}
    )
    assert response.status_code == 400
