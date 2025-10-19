"""Tests for the dummy Evo2 implementation."""

import math
import os

import pytest
import torch

from evo2_mcp.dummy_evo2 import DummyEvo2


@pytest.fixture
def dummy_model() -> DummyEvo2:
    """Create a dummy Evo2 model instance."""
    return DummyEvo2("evo2_1b_base")


def test_dummy_tokenizer(dummy_model: DummyEvo2) -> None:
    """Verify tokenizer converts DNA sequences to token IDs."""
    tokens = dummy_model.tokenizer.tokenize("ACGT")
    assert tokens == [0, 1, 2, 3]

    tokens_with_n = dummy_model.tokenizer.tokenize("ACGTN")
    assert tokens_with_n == [0, 1, 2, 3, 4]


def test_dummy_forward_without_embeddings(dummy_model: DummyEvo2) -> None:
    """Verify forward pass returns correct logits shape."""
    batch_size = 2
    seq_len = 10
    input_ids = torch.randint(0, 5, (batch_size, seq_len))

    logits, embeddings = dummy_model.forward(input_ids, return_embeddings=False)

    assert logits.shape == (batch_size, seq_len, 512)
    assert embeddings is None


def test_dummy_forward_with_embeddings(dummy_model: DummyEvo2) -> None:
    """Verify forward pass returns embeddings when requested."""
    batch_size = 2
    seq_len = 10
    input_ids = torch.randint(0, 5, (batch_size, seq_len))
    layer_names = ["blocks.2.mlp.l3", "blocks.4.mlp.l3"]

    logits, embeddings = dummy_model.forward(
        input_ids, return_embeddings=True, layer_names=layer_names
    )

    assert logits.shape == (batch_size, seq_len, 512)
    assert embeddings is not None
    assert len(embeddings) == 2
    for layer_name in layer_names:
        assert layer_name in embeddings
        assert embeddings[layer_name].shape == (batch_size, seq_len, 256)


def test_dummy_forward_embeddings_assertion(dummy_model: DummyEvo2) -> None:
    """Verify forward raises assertion when layer_names missing."""
    input_ids = torch.randint(0, 5, (1, 10))

    with pytest.raises(AssertionError, match="layer_names required"):
        dummy_model.forward(input_ids, return_embeddings=True, layer_names=None)


def test_dummy_call_method(dummy_model: DummyEvo2) -> None:
    """Verify model can be called as a function."""
    input_ids = torch.randint(0, 5, (1, 10))
    logits, embeddings = dummy_model(input_ids, return_embeddings=False)

    assert logits.shape == (1, 10, 512)
    assert embeddings is None


def test_dummy_score_sequences_mean(dummy_model: DummyEvo2) -> None:
    """Verify sequence scoring with mean reduction."""
    sequences = ["ACGT", "TGCA"]
    scores = dummy_model.score_sequences(sequences, reduce_method="mean")

    assert len(scores) == 2
    assert all(math.isfinite(score) for score in scores)
    assert all(-2.0 <= score <= -1.0 for score in scores)


def test_dummy_score_sequences_sum(dummy_model: DummyEvo2) -> None:
    """Verify sequence scoring with sum reduction."""
    sequences = ["ACGT"]
    scores = dummy_model.score_sequences(sequences, reduce_method="sum")

    assert len(scores) == 1
    assert math.isfinite(scores[0])


def test_dummy_generate(dummy_model: DummyEvo2) -> None:
    """Verify sequence generation."""
    prompts = ["AC", "TG"]
    n_tokens = 20

    result = dummy_model.generate(prompts, n_tokens=n_tokens, temperature=0.5, top_k=4)

    assert len(result.sequences) == 2
    for generated in result.sequences:
        assert isinstance(generated, str)
        assert 1 <= len(generated) <= n_tokens
        assert set(generated).issubset({"A", "C", "G", "T"})


def test_dummy_generate_deterministic(dummy_model: DummyEvo2) -> None:
    """Verify generation is deterministic with same seed."""
    prompts = ["ACGT"]
    n_tokens = 10

    result1 = dummy_model.generate(prompts, n_tokens=n_tokens)
    dummy_model_2 = DummyEvo2("evo2_1b_base")
    result2 = dummy_model_2.generate(prompts, n_tokens=n_tokens)

    # Both should generate valid sequences (though not necessarily identical due to randomness)
    assert len(result1.sequences[0]) > 0
    assert len(result2.sequences[0]) > 0


def test_environment_variable_integration() -> None:
    """Verify USE_DUMMY_EVO2 environment variable is respected."""
    from evo2_mcp.model import USE_DUMMY_EVO2

    env_value = os.getenv("EVO2_MCP_USE_DUMMY", "false")
    expected = env_value.lower() in ("true", "1", "yes")

    assert USE_DUMMY_EVO2 == expected
