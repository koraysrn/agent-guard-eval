"""Tests for :mod:`agent_guard_eval.logging`."""

from __future__ import annotations

import logging

from agent_guard_eval.logging import RedactingFormatter, get_logger


def test_get_logger_returns_same_instance() -> None:
    logger1 = get_logger("agent_guard_eval.test.logging")
    logger2 = get_logger("agent_guard_eval.test.logging")
    assert logger1 is logger2
    assert len(logger1.handlers) >= 1


def test_redacting_formatter_masks_secrets() -> None:
    formatter = RedactingFormatter()
    record = logging.LogRecord(
        name="x", level=logging.WARNING, pathname="path", lineno=1,
        msg="api_key=SECRET123 happened", args=None, exc_info=None,
    )
    formatted = formatter.format(record)
    assert "SECRET123" not in formatted
    assert "api_key=***" in formatted


def test_redact_method() -> None:
    formatter = RedactingFormatter()
    text = "token=abc password=hunter2 ok"
    redacted = formatter.redact(text)
    assert "abc" not in redacted
    assert "hunter2" not in redacted
    assert "ok" in redacted


def test_non_sensitive_text_untouched() -> None:
    formatter = RedactingFormatter()
    assert formatter.redact("Sharpe ratio is 1.5") == "Sharpe ratio is 1.5"
