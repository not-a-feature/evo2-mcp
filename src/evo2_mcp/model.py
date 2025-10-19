"""Utilities for managing Evo 2 model instances used by the MCP tools."""

from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - used for static type checkers only
    from evo2 import Evo2  # type: ignore[import]  # noqa: F401

DEFAULT_CHECKPOINT = os.getenv("EVO2_MCP_CHECKPOINT", "evo2_1b_base")
USE_DUMMY_EVO2 = os.getenv("EVO2_MCP_USE_DUMMY", "false").lower() in ("true", "1", "yes")

_MODEL_LOCK = threading.Lock()


@dataclass(frozen=True, slots=True)
class ModelHandle:
    """Cached Evo 2 model with checkpoint metadata."""

    checkpoint: str
    model: Any


def get_evo2_model(checkpoint: Optional[str] = None) -> ModelHandle:
    """Return cached Evo 2 model for the requested checkpoint."""

    resolved_checkpoint = checkpoint or DEFAULT_CHECKPOINT
    model = _load_model(resolved_checkpoint)
    return ModelHandle(checkpoint=resolved_checkpoint, model=model)


@lru_cache(maxsize=8)
def _load_model(checkpoint: str) -> Any:
    """Load and cache model with thread-safe initialization."""
    with _MODEL_LOCK:
        return _create_model(checkpoint)


def _create_model(checkpoint: str) -> Any:
    """Instantiate Evo 2 model for the given checkpoint."""
    if USE_DUMMY_EVO2:
        print("WARNING: Using dummy Evo2 implementation (EVO2_MCP_USE_DUMMY=true).")
        print("Results are random and should not be used for any analysis.")
        from evo2_mcp.dummy_evo2 import DummyEvo2

        return DummyEvo2(checkpoint)

    try:
        from evo2 import Evo2  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise RuntimeError(
            "The 'evo2' package is required to use the evo2-mcp server. Install evo2 before running the server."
        ) from exc

    return Evo2(checkpoint)
