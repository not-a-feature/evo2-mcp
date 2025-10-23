"""MCP tools for Evo 2 sequence operations.

This module implements the core MCP (Model Context Protocol) tools for genomic sequence
analysis using the Evo 2 foundation model. It provides functionality for:

- Scoring DNA sequences to evaluate their likelihood under the model
- Generating new DNA sequences conditioned on prompts
- Extracting learned representations (embeddings) from intermediate model layers
- Predicting variant effects (SNP scoring)


Supported Checkpoints
---------------------
The following Evo 2 model checkpoints are officially supported by this package:
- evo2_7b: 7B parameters, 1M context
- evo2_40b: 40B parameters, 1M context (requires multiple GPUs)
- evo2_7b_base: 7B parameters, 8K context
- evo2_40b_base: 40B parameters, 8K context
- evo2_1b_base: 1B parameters, 8K context

All public functions are registered as MCP tools via the @mcp.tool decorator.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import json
from pathlib import Path

import torch  # type: ignore[import]

from evo2_mcp.mcp import mcp
from evo2_mcp.model import ModelHandle, get_evo2_model

KNOWN_CHECKPOINTS: Dict[str, str] = {
    "evo2_7b": "7B parameter model with 1M context",
    "evo2_40b": "40B parameter model with 1M context (requires multiple GPUs)",
    "evo2_7b_base": "7B parameter model with 8K context",
    "evo2_40b_base": "40B parameter model with 8K context",
    "evo2_1b_base": "1B parameter model with 8K context",
    # Removed/unsupported checkpoints (not listed here):
    # - evo2_7b_262k
    # - evo2_7b_microviridae
}

_LAYERS_INDEX_CACHE: Optional[Dict[str, Any]] = None


def _load_layers_index() -> Dict[str, Any]:
    """Load and cache the layers.json index located alongside this module."""
    global _LAYERS_INDEX_CACHE
    if _LAYERS_INDEX_CACHE is None:
        json_path = Path(__file__).with_name("layers.json")
        with json_path.open("r", encoding="utf-8") as f:
            _LAYERS_INDEX_CACHE = json.load(f)
        assert isinstance(
            _LAYERS_INDEX_CACHE, dict
        ), "layers.json must contain a JSON object at top level"
    return _LAYERS_INDEX_CACHE


@mcp.tool
def list_available_checkpoints() -> List[Dict[str, str]]:
    """List supported Evo 2 checkpoints with descriptions.

    Retrieves all available Evo 2 model checkpoints that can be used for
    sequence scoring, embedding, and generation. Each checkpoint is described
    with its size and context length capabilities.

    Returns:
        List of dictionaries, each containing:
            - name: The identifier string for the checkpoint
            - description: Human-readable description of the model specifications
    """
    return [
        {"name": name, "description": description}
        for name, description in KNOWN_CHECKPOINTS.items()
    ]


@mcp.tool
def get_embedding_layers(
    checkpoint: str,
    which: str = "recommended",
) -> Dict[str, Any]:
    """Get available layers for embedding extraction from Evo 2 model.

    Returns a list of layer names that can be used to extract sequence embeddings
    from the specified Evo 2 checkpoint. Different layers encode varying levels of
    biological abstraction. Larger models tend to have more nuanced representations but require
    more computational resources. For supervised classification tasks (e.g., variant effect
    prediction), intermediate layers like Block 20 (40B model) often perform best. For mechanistic
    interpretability (e.g., SAE training), deeper layers like Layer 26 are commonly used. For
    probing tasks, top-level layers (e.g., blocks.26 in 7B model) may be optimal.

    Args:
        checkpoint: Model checkpoint identifier. See `list_available_checkpoints()` for options.
        which: Selection switch. "recommended" returns a curated subset of layers suitable for
            common downstream tasks; "all" returns every available layer from the model.

    Returns:
        Dictionary containing:
            - checkpoint: The checkpoint identifier
            - layers: List of layer names available for embedding extraction
            - info: Information about layer selection for different tasks

    Example:
        >>> layers = get_embedding_layers("evo2_7b")
        >>> print(f"Layers (recommended): {layers['layers']}")
        >>> layers_all = get_embedding_layers("evo2_7b", which="all")
        >>> print(f"Total layers: {len(layers_all['layers'])}")
    """
    assert which in ("recommended", "all"), "'which' must be either 'recommended' or 'all'"

    handle = get_evo2_model(checkpoint)

    layers_index = _load_layers_index()
    assert (
        handle.checkpoint in layers_index
    ), f"Checkpoint '{handle.checkpoint}' not found in layers index JSON"

    entry = layers_index[handle.checkpoint]
    assert "layers" in entry and isinstance(
        entry["layers"], list
    ), f"Malformed layers index for checkpoint '{handle.checkpoint}'"

    available_layers: List[str] = entry["layers"]

    # Default to recommended subset unless user asks for all

    selected_layers = (
        available_layers
        if which == "all"
        else _select_recommended_layers(available_layers, handle.checkpoint)
    )

    layer_info = (
        "Layer selection depends on the task. Recommended subset includes early, mid, and deep MLP layers "
        "(e.g., blocks.2.mlp.l3, blocks.13.mlp.l3, blocks.20.mlp.l3) along with encoder norms. "
        "Use which='all' to access every available layer."
    )

    return {
        "checkpoint": handle.checkpoint,
        "layers": selected_layers,
        "info": layer_info,
    }


def _select_recommended_layers(available_layers: List[str], checkpoint: str) -> List[str]:
    """Return a curated subset of useful layers if present in the given checkpoint."""
    # Curated candidates spanning early, middle, and deeper network regions
    candidates = [
        "embedding_layer",
        "blocks.2.mlp.l3",
        "blocks.13.mlp.l3",
        "blocks.20.mlp.l3",
        "blocks.26.mlp.l3",
    ]

    selected = [name for name in candidates if name in available_layers]
    assert selected, f"No recommended layers found for checkpoint '{checkpoint}'"
    return selected


@mcp.tool
def score_sequence(
    sequence: str,
    checkpoint: Optional[str] = None,
    reduce_method: str = "mean",
) -> Dict[str, Any]:
    """Compute log probabilities for DNA sequence under Evo 2 model.

    Evaluates the likelihood of a DNA sequence under the Evo 2 language model.
    Returns the model's log probability score for the entire sequence, which can
    be reduced using either mean or sum aggregation.

    Args:
        sequence: DNA sequence to score. Should contain standard IUPAC nucleotides (A, C, G, T, N).
        checkpoint: Model checkpoint identifier. If None, uses the default checkpoint.
            See `list_available_checkpoints()` for available options.
        reduce_method: Method for aggregating per-token scores. Must be either "mean"
            (average log probability across all tokens) or "sum" (sum of all log probabilities).

    Returns:
        Dictionary containing:
            - checkpoint: The checkpoint identifier used
            - sequence: The normalized input sequence
            - reduce_method: The reduction method applied
            - scores: List of computed score values (typically length 1)

    Raises:
        AssertionError: If sequence is empty or reduce_method is not "mean" or "sum".

    Example:
        >>> scores = score_sequence("ATCGATCG")
        >>> print(f"Score: {scores['scores'][0]}")
    """
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
    """Return intermediate Evo 2 embeddings for DNA sequence.

    Extracts feature representations from a specified layer of the Evo 2 model
    for a given DNA sequence. The embeddings capture the model's learned
    representations and can be used for downstream analysis or as features
    for other tasks.

    Args:
        sequence: DNA sequence to embed. Should contain standard IUPAC nucleotides (A, C, G, T).
        checkpoint: Model checkpoint identifier. If None, uses the default checkpoint.
            See `list_available_checkpoints()` for available options.
        layer_name: Name of the model layer from which to extract embeddings.
            Common choices include intermediate MLP layers and attention blocks.

    Returns:
        Dictionary containing:
            - checkpoint: The checkpoint identifier used
            - sequence: The normalized input sequence
            - layer_name: The layer from which embeddings were extracted
            - embedding: 2D list of embedding vectors (shape: [sequence_length, embedding_dim])

    Raises:
        AssertionError: If sequence or layer_name are empty strings.

    Example:
        >>> embeddings = embed_sequence("ATCGATCG")
        >>> embedding_matrix = embeddings['embedding']
        >>> print(f"Embedding shape: {len(embedding_matrix)} tokens")
    """
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
    """Generate DNA sequence continuation using Evo 2.

    Generates new DNA sequence tokens conditioned on a given prompt sequence
    using the Evo 2 language model. The generation process uses nucleus sampling
    (top-k) for controlled diversity.

    Args:
        prompt: Starting DNA sequence to condition generation. Should contain standard
            IUPAC nucleotides (A, C, G, T, N).
        checkpoint: Model checkpoint identifier. If None, uses the default checkpoint.
            See `list_available_checkpoints()` for available options.
        n_tokens: Number of new tokens to generate. Must be a positive integer.
        temperature: Sampling temperature controlling randomness. Higher values (>1.0) increase
            diversity; lower values (<1.0) make generation more deterministic. Must be greater than 0.
        top_k: Number of highest probability nucleotides to sample from at each step.
            Must be positive. Typical values: 5 (all nucleotides including N), 4 (more constrained).

    Returns:
        Dictionary containing:
            - checkpoint: The checkpoint identifier used
            - prompt: The normalized input prompt sequence
            - generated_sequence: The newly generated DNA sequence
            - n_tokens: Number of tokens generated
            - temperature: Temperature value used
            - top_k: Top-k value used

    Raises:
        AssertionError: If prompt is empty, n_tokens <= 0, temperature <= 0, or top_k <= 0.

    Example:
        >>> result = generate_sequence("ATCGATCG", n_tokens=100, temperature=0.8)
        >>> full_sequence = result['prompt'] + result['generated_sequence']
        >>> print(f"Generated sequence: {full_sequence}")
    """
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

    This tool is useful for variant effect prediction, where the score delta indicates
    how much the mutation changes the model's likelihood of the sequence. Negative deltas
    indicate the mutation decreases likelihood; positive deltas increase it.

    Args:
        sequence: Reference DNA sequence. Must be at least 3 nucleotides long to have a
            well-defined center position. Should contain standard IUPAC nucleotides (A, C, G, T, N).
        alternative_allele: Alternative nucleotide at the center position. Must be a single
            nucleotide (one of A, C, G, T, N) that differs from the reference nucleotide at the center.
        checkpoint: Model checkpoint identifier. If None, uses the default checkpoint.
            See `list_available_checkpoints()` for available options.
        reduce_method: Method for aggregating per-token scores. Must be either "mean"
            (average log probability across all tokens) or "sum" (sum of all log probabilities).

    Returns:
        Dictionary containing:
            - checkpoint: The checkpoint identifier used
            - original_sequence: The input reference sequence (uppercase)
            - mutated_sequence: The sequence with the mutation applied at center position
            - center_position: Index of the mutated position (0-indexed)
            - reference_allele: The original nucleotide at the center position
            - alternative_allele: The alternative nucleotide used
            - reduce_method: The reduction method applied
            - original_score: Log probability score of the reference sequence
            - mutated_score: Log probability score of the mutated sequence
            - score_delta: Difference (mutated_score - original_score). Indicates mutation effect.

    Raises:
        AssertionError: If sequence length < 3, alternative_allele is not a single valid nucleotide,
            sequence contains invalid nucleotides, or alternative_allele matches the reference nucleotide.

    Example:
        >>> result = score_snp("ATCGATCG", "A")  # Center is T, mutate to A
        >>> print(f"Score delta: {result['score_delta']}")
        >>> print(f"Original: {result['original_sequence']}")
        >>> print(f"Mutated: {result['mutated_sequence']}")
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
    """Compute sequence log probabilities using Evo 2 model.

    Internal helper function that interfaces with the Evo 2 model to compute
    per-token or aggregated log probabilities for a given DNA sequence.

    Parameters
    ----------
    handle : ModelHandle
        Model handle containing the loaded Evo 2 model and configuration.
    sequence : str
        DNA sequence to score. Expected to be normalized (uppercase, valid nucleotides).
    reduce_method : str, default="mean"
        Aggregation method for per-token scores:
        - "mean": Average log probability across all tokens
        - "sum": Sum of all log probabilities

    Returns
    -------
    List[float]
        List of aggregated score values. For typical usage, contains a single score.
    """
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
    """Extract intermediate layer embeddings from Evo 2 model.

    Internal helper function that extracts feature representations from a
    specified layer of the Evo 2 model. The sequence is tokenized, passed through
    the model, and embeddings are extracted and converted to nested lists.

    Parameters
    ----------
    handle : ModelHandle
        Model handle containing the loaded Evo 2 model and tokenizer.
    sequence : str
        DNA sequence to embed. Expected to be normalized (uppercase, valid nucleotides).
    layer_name : str
        Name of the model layer from which to extract embeddings.

    Returns
    -------
    List[List[float]]
        2D list of embeddings where each inner list is the embedding vector
        for a single token. Shape is [sequence_length, embedding_dim].

    Raises
    ------
    AssertionError
        If the sequence doesn't tokenize to at least one token or the requested
        layer is not found in the model's embeddings.
    """
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
    """Generate sequence continuation using Evo 2 model.

    Internal helper function that interfaces with the Evo 2 model to generate
    new sequence tokens conditioned on a prompt. Uses nucleus sampling (top-k)
    for controlled diversity during generation.

    Parameters
    ----------
    handle : ModelHandle
        Model handle containing the loaded Evo 2 model.
    prompt : str
        Starting DNA sequence to condition generation.
        Expected to be normalized (uppercase, valid nucleotides).
    n_tokens : int
        Number of new tokens to generate. Must be positive.
    temperature : float
        Sampling temperature. Higher values increase diversity,
        lower values make generation more deterministic.
    top_k : int
        Number of highest probability nucleotides to sample from.

    Returns
    -------
    str
        The newly generated DNA sequence (continuation of the prompt).
        Does not include the original prompt in the output.
    """
    generation_kwargs: Dict[str, Any] = {
        "prompt_seqs": [prompt],
        "n_tokens": n_tokens,
        "temperature": temperature,
        "top_k": top_k,
    }

    output = handle.model.generate(**generation_kwargs)
    return output.sequences[0]
