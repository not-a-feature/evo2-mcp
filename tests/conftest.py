"""Test configuration and fixtures."""

import pytest  # type: ignore[import]

from evo2_mcp.model import ModelHandle

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(autouse=True)
def fake_evo2_runtime(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
) -> None:
    """Mock Evo 2 operations for fast testing."""
    if request.node.get_closest_marker("real_evo2"):
        return

    from evo2_mcp.tools import _evo2

    def _fake_handle(checkpoint: str | None = None) -> ModelHandle:
        effective_checkpoint = checkpoint or "evo2_1b_base"
        return ModelHandle(checkpoint=effective_checkpoint, model=object())

    monkeypatch.setattr(_evo2, "get_evo2_model", _fake_handle)
    monkeypatch.setattr(
        _evo2,
        "_compute_sequence_score",
        lambda handle, seq, reduce_method: [0.5],
    )

    monkeypatch.setattr(
        _evo2,
        "_compute_sequence_embedding",
        lambda handle, seq, layer: [0.1, 0.2, 0.3],
    )

    monkeypatch.setattr(
        _evo2,
        "_run_generation",
        lambda handle, prompt, n_tokens, temperature, top_k: f"{prompt}-mock",
    )
