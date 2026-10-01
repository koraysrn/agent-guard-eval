"""Optional integrations with external frameworks.

LangChain and FastAPI adapters are only exported when their optional dependencies are
installed; importing this package never fails for missing extras.
"""

from __future__ import annotations

__all__: list[str] = []

try:
    from .fastapi import NumericGuardMiddleware, create_guard_dependency

    __all__ += ["NumericGuardMiddleware", "create_guard_dependency"]
except ImportError:  # pragma: no cover - depends on optional dependency
    pass

try:
    from .langchain import NumericGuardTool, make_guard_node

    __all__ += ["NumericGuardTool", "make_guard_node"]
except ImportError:  # pragma: no cover - depends on optional dependency
    pass
