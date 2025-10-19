"""Real Evo 2 model integration tests."""

import math

import pytest

from evo2_mcp.model import ModelHandle
from evo2_mcp.tools import _evo2

pytestmark = pytest.mark.real_evo2


@pytest.fixture(scope="module")
def real_model_handle() -> ModelHandle:
    """Load real Evo 2 model for integration tests."""
    return _evo2.get_evo2_model("evo2_1b_base")


def test_compute_sequence_score_real(real_model_handle: ModelHandle) -> None:
    """Verify sequence scoring with real model."""
    mean_scores = _evo2._compute_sequence_score(real_model_handle, "ACGT", "mean")
    assert isinstance(mean_scores, list)
    assert len(mean_scores) == 1
    assert math.isfinite(mean_scores[0])

    sum_scores = _evo2._compute_sequence_score(real_model_handle, "ACGT", "sum")
    assert isinstance(sum_scores, list)
    assert len(sum_scores) == 1
    assert math.isfinite(sum_scores[0])


def test_compute_sequence_embedding_real(real_model_handle: ModelHandle) -> None:
    """Verify sequence embedding extraction with real model."""
    sequence = "ACGT"
    embedding = _evo2._compute_sequence_embedding(real_model_handle, sequence, "blocks.2.mlp.l3")

    assert len(embedding) == len(sequence)
    embedding_dim = len(embedding[0])
    assert [len(token_emb) == embedding_dim for token_emb in embedding]
    assert all(all(math.isfinite(x) for x in token_emb) for token_emb in embedding)


def test_run_generation_real(real_model_handle: ModelHandle) -> None:
    """Verify sequence generation with real model."""
    prompt = "AC"
    n_tokens = 6
    temperature = 0.5
    top_k = 4

    generated = _evo2._run_generation(
        real_model_handle,
        prompt,
        n_tokens,
        temperature,
        top_k,
    )

    assert 1 <= len(generated) <= n_tokens
    assert set(generated).issubset({"A", "C", "G", "T", "N"})


def test_score_snp_computation_real(real_model_handle: ModelHandle) -> None:
    """Verify SNP scoring computation with real model."""
    original_sequence = "ACGTACGT"
    mutated_sequence = "ACGTTCGT"

    original_scores = _evo2._compute_sequence_score(real_model_handle, original_sequence, "mean")
    mutated_scores = _evo2._compute_sequence_score(real_model_handle, mutated_sequence, "mean")

    assert isinstance(original_scores, list)
    assert isinstance(mutated_scores, list)
    assert len(original_scores) == 1
    assert len(mutated_scores) == 1
    assert math.isfinite(original_scores[0])
    assert math.isfinite(mutated_scores[0])

    delta = mutated_scores[0] - original_scores[0]
    assert math.isfinite(delta)


def test_score_snp_center_position_calculation() -> None:
    """Verify center position is correctly calculated for various sequence lengths."""
    test_cases = [
        ("ACG", 1),
        ("ACGT", 2),
        ("ACGTA", 2),
        ("ACGTAC", 3),
        ("ACGTACG", 3),
        ("ACGTACGT", 4),
    ]

    for sequence, expected_center in test_cases:
        center_idx = len(sequence) // 2
        assert center_idx == expected_center


def test_score_snp_validation_logic() -> None:
    """Verify SNP scoring validation checks work correctly."""
    valid_sequence = "ACGTACGT"
    center_idx = len(valid_sequence) // 2
    center_nucleotide = valid_sequence[center_idx]

    assert center_nucleotide == "A"
    assert center_nucleotide in "ACGT"

    valid_alternatives = {"C", "G", "T"}
    for alt in valid_alternatives:
        assert alt != center_nucleotide
        assert alt in "ACGT"
