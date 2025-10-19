"""MCP tools for Evo 2 sequence operations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import torch  # type: ignore[import]

from evo2_mcp.mcp import mcp
from evo2_mcp.model import ModelHandle, get_evo2_model

KNOWN_CHECKPOINTS: Dict[str, str] = {
    "evo2_7b": "7B parameter model with 1M context",
    "evo2_40b": "40B parameter model with 1M context (requires multiple GPUs)",
    "evo2_7b_base": "7B parameter model with 8K context",
    "evo2_40b_base": "40B parameter model with 8K context",
    "evo2_1b_base": "1B parameter model with 8K context",
    "evo2_7b_262k": "7B parameter model with 262K context",
    "evo2_7b_microviridae": "7B parameter base model fine-tuned on Microviridae genomes",
}


@mcp.tool
def list_available_checkpoints() -> List[Dict[str, str]]:
    """List supported Evo 2 checkpoints with descriptions."""
    return [
        {"name": name, "description": description}
        for name, description in KNOWN_CHECKPOINTS.items()
    ]


@mcp.tool
def score_sequence(
    sequence: str,
    checkpoint: Optional[str] = None,
    reduce_method: str = "mean",
) -> Dict[str, Any]:
    """Compute log probabilities for DNA sequence under Evo 2 model."""
    assert isinstance(sequence, str) and sequence.strip(), "'sequence' must be a non-empty string"
    assert reduce_method in ("mean", "sum"), "'reduce_method' must be either 'mean' or 'sum'"

    normalized_sequence = sequence.strip()
    handle = get_evo2_model(checkpoint)
    scores = _compute_sequence_score(handle, normalized_sequence, reduce_method)

    return {
        "checkpoint": handle.checkpoint,
        "sequence": normalized_sequence,
        "reduce_method": reduce_method,
        "scores": scores,
    }


@mcp.tool
def embed_sequence(
    sequence: str,
    checkpoint: Optional[str] = None,
    layer_name: str = "blocks.2.mlp.l3",
) -> Dict[str, Any]:
    """Return intermediate Evo 2 embeddings for DNA sequence."""
    assert isinstance(sequence, str) and sequence.strip(), "'sequence' must be a non-empty string"
    assert isinstance(layer_name, str) and layer_name, "'layer_name' must be a non-empty string"

    normalized_sequence = sequence.strip()
    handle = get_evo2_model(checkpoint)
    embedding = _compute_sequence_embedding(handle, normalized_sequence, layer_name)

    return {
        "checkpoint": handle.checkpoint,
        "sequence": normalized_sequence,
        "layer_name": layer_name,
        "embedding": embedding,
    }


@mcp.tool
def generate_sequence(
    prompt: str,
    checkpoint: Optional[str] = None,
    n_tokens: int = 400,
    temperature: float = 1.0,
    top_k: int = 4,
) -> Dict[str, Any]:
    """Generate DNA sequence continuation using Evo 2."""
    assert isinstance(prompt, str) and prompt.strip(), "'prompt' must be a non-empty string"
    assert isinstance(n_tokens, int) and n_tokens > 0, "'n_tokens' must be a positive integer"
    assert temperature > 0, "'temperature' must be greater than 0"
    assert top_k > 0, "'top_k' must be positive"

    normalized_prompt = prompt.strip()
    handle = get_evo2_model(checkpoint)
    generated = _run_generation(handle, normalized_prompt, n_tokens, temperature, top_k)

    return {
        "checkpoint": handle.checkpoint,
        "prompt": normalized_prompt,
        "generated_sequence": generated,
        "n_tokens": n_tokens,
        "temperature": temperature,
        "top_k": top_k,
    }


@mcp.tool
def score_snp(
    sequence: str,
    alternative_allele: str,
    checkpoint: Optional[str] = None,
    reduce_method: str = "mean",
) -> Dict[str, Any]:
    """Score the effect of a SNP mutation at the center position of a DNA sequence.

    Computes log probabilities for both the original sequence and the sequence with
    the center nucleotide replaced by the alternative allele, then returns the delta.
    Recommended sequence length: max_context - 1 for best performance.
    """
    assert isinstance(sequence, str) and sequence.strip(), "'sequence' must be a non-empty string"
    assert (
        isinstance(alternative_allele, str) and alternative_allele.strip()
    ), "'alternative_allele' must be a non-empty string"
    assert reduce_method in ("mean", "sum"), "'reduce_method' must be either 'mean' or 'sum'"

    normalized_sequence = sequence.strip().upper()
    normalized_alt = alternative_allele.strip().upper()

    assert len(normalized_sequence) >= 3, "'sequence' must be at least 3 nucleotides long"
    assert len(normalized_alt) == 1, "'alternative_allele' must be a single nucleotide"
    assert normalized_alt in "ACGT", "'alternative_allele' must be one of A, C, G, T"

    center_idx = len(normalized_sequence) // 2
    center_nucleotide = normalized_sequence[center_idx]

    assert (
        center_nucleotide in "ACGT"
    ), f"Center nucleotide '{center_nucleotide}' at position {center_idx} is not a valid DNA base"
    assert (
        center_nucleotide != normalized_alt
    ), f"Alternative allele '{normalized_alt}' must differ from center nucleotide '{center_nucleotide}'"

    handle = get_evo2_model(checkpoint)

    original_scores = _compute_sequence_score(handle, normalized_sequence, reduce_method)
    mutated_sequence = (
        normalized_sequence[:center_idx] + normalized_alt + normalized_sequence[center_idx + 1 :]
    )
    mutated_scores = _compute_sequence_score(handle, mutated_sequence, reduce_method)

    assert len(original_scores) == 1, "Expected single score for original sequence"
    assert len(mutated_scores) == 1, "Expected single score for mutated sequence"

    original_score = original_scores[0]
    mutated_score = mutated_scores[0]
    delta = mutated_score - original_score

    return {
        "checkpoint": handle.checkpoint,
        "original_sequence": normalized_sequence,
        "mutated_sequence": mutated_sequence,
        "center_position": center_idx,
        "reference_allele": center_nucleotide,
        "alternative_allele": normalized_alt,
        "reduce_method": reduce_method,
        "original_score": original_score,
        "mutated_score": mutated_score,
        "score_delta": delta,
    }


def _compute_sequence_score(
    handle: ModelHandle, sequence: str, reduce_method: str = "mean"
) -> List[float]:
    """Compute sequence log probabilities using Evo 2 model."""
    scores = handle.model.score_sequences(
        seqs=[sequence],
        batch_size=1,
        prepend_bos=False,
        reduce_method=reduce_method,
        average_reverse_complement=False,
    )

    assert isinstance(scores, list), "Unexpected return from Evo2.score_sequences; expected a list"
    return scores


def _compute_sequence_embedding(
    handle: ModelHandle, sequence: str, layer_name: str
) -> List[List[float]]:
    """Extract intermediate layer embeddings from Evo 2 model."""
    tokens = handle.model.tokenizer.tokenize(sequence)
    assert tokens, "Sequence must tokenize to at least one token for embeddings"

    input_ids = torch.tensor(tokens, dtype=torch.long).unsqueeze(0)
    if torch.cuda.is_available():
        input_ids = input_ids.to("cuda:0")

    with torch.no_grad():
        outputs, embeddings = handle.model(
            input_ids, return_embeddings=True, layer_names=[layer_name]
        )

    assert layer_name in embeddings, f"Layer '{layer_name}' not found in returned embeddings"

    tensor = embeddings[layer_name][0].detach().float().cpu()
    return tensor.tolist()


def _run_generation(
    handle: ModelHandle,
    prompt: str,
    n_tokens: int,
    temperature: float,
    top_k: int,
) -> str:
    """Generate sequence continuation using Evo 2 model."""
    generation_kwargs: Dict[str, Any] = {
        "prompt_seqs": [prompt],
        "n_tokens": n_tokens,
        "temperature": temperature,
        "top_k": top_k,
    }

    output = handle.model.generate(**generation_kwargs)
    return output.sequences[0]
