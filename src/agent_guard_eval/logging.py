"""Structured logger with sensitive-data redaction.

For security, the ``RedactingFormatter`` prevents API keys, tokens and passwords from
leaking into log records.
"""

from __future__ import annotations

import logging
import re

# (pattern, replacement) pairs; captured secrets are masked with "***".
_SENSITIVE_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"(?i)(api[_-]?key|token|secret|password|passwd)\s*[:=]\s*\S+", r"\1=***"),
    (r"(?i)(authorization|bearer)\s*[:=]?\s*\S+", r"\1=***"),
)

_DEFAULT_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


class RedactingFormatter(logging.Formatter):
    """Formatter that masks sensitive fields in log records."""

    def __init__(self, fmt: str = _DEFAULT_FORMAT) -> None:
        super().__init__(fmt)

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        for pattern, replacement in _SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message)
        return message

    def redact(self, text: str) -> str:
        """Return the given text with sensitive patterns masked."""
        result = text
        for pattern, replacement in _SENSITIVE_PATTERNS:
            result = re.sub(pattern, replacement, result)
        return result


def get_logger(name: str = "agent_guard_eval") -> logging.Logger:
    """Return the logger with the given name, configuring it once on first call.

    Repeated calls return the same, already-configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(RedactingFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        logger.propagate = False
    return logger
