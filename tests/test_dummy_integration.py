"""Integration tests using the dummy Evo2 implementation."""

import math
import os

import pytest

from evo2_mcp.tools import _evo2

pytestmark = [
    pytest.mark.skipif(
        os.getenv("EVO2_MCP_USE_DUMMY", "false").lower() not in ("true", "1", "yes"),
        reason="These tests require EVO2_MCP_USE_DUMMY=true to verify dummy implementation",
    ),
    pytest.mark.real_evo2,
]


def test_dummy_integration_score_sequences() -> None:
    """Verify sequence scoring works with dummy model."""
    handle = _evo2.get_evo2_model("evo2_1b_base")

    scores = _evo2._compute_sequence_score(handle, "ACGT", "mean")

    assert isinstance(scores, list)
    assert len(scores) == 1
    assert math.isfinite(scores[0])
    assert -2.0 <= scores[0] <= -1.0


def test_dummy_integration_embeddings() -> None:
    """Verify embedding extraction works with dummy model."""
    handle = _evo2.get_evo2_model("evo2_1b_base")
    sequence = "ACGT"
    layer_name = "blocks.2.mlp.l3"

    embedding = _evo2._compute_sequence_embedding(handle, sequence, layer_name)

    assert isinstance(embedding, list)
    assert len(embedding) == len(sequence)
    embedding_dim = len(embedding[0])
    assert embedding_dim > 0
    assert all(len(token_emb) == embedding_dim for token_emb in embedding)
    assert all(all(math.isfinite(x) for x in token_emb) for token_emb in embedding)


def test_dummy_integration_generation() -> None:
    """Verify sequence generation works with dummy model."""
    handle = _evo2.get_evo2_model("evo2_1b_base")
    prompt = "AC"
    n_tokens = 10

    generated = _evo2._run_generation(handle, prompt, n_tokens, temperature=1.0, top_k=4)

    assert isinstance(generated, str)
    assert 1 <= len(generated) <= n_tokens
    assert set(generated).issubset({"A", "C", "G", "T"})


def test_dummy_integration_snp_scoring() -> None:
    """Verify SNP scoring works end-to-end with dummy model."""
    original_sequence = "ACGTACGT"
    mutated_sequence = "ACGTTCGT"

    handle = _evo2.get_evo2_model("evo2_1b_base")

    original_scores = _evo2._compute_sequence_score(handle, original_sequence, "mean")
    mutated_scores = _evo2._compute_sequence_score(handle, mutated_sequence, "mean")

    assert isinstance(original_scores, list)
    assert isinstance(mutated_scores, list)
    assert len(original_scores) == 1
    assert len(mutated_scores) == 1
    assert math.isfinite(original_scores[0])
    assert math.isfinite(mutated_scores[0])

    delta = mutated_scores[0] - original_scores[0]
    assert math.isfinite(delta)
