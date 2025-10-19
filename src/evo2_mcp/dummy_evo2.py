"""Dummy implementation of Evo2 interface for testing without model dependencies."""

from __future__ import annotations

import random
from typing import Dict, List, Tuple

import torch


class DummyTokenizer:
    """Minimal tokenizer that maps DNA characters to integers."""

    def __init__(self, vocab_size: int):
        self.vocab_size = vocab_size
        self._char_to_id = {"A": 0, "C": 1, "G": 2, "T": 3, "N": 4}

    def tokenize(self, sequence: str) -> List[int]:
        """Convert sequence string to list of token IDs."""
        return [self._char_to_id.get(char.upper(), 4) for char in sequence]


class DummyGeneration:
    """Container for generation results."""

    def __init__(self, sequences: List[str]):
        self.sequences = sequences


class DummyEvo2:
    """Dummy Evo2 model that mimics the real interface without loading actual models."""

    def __init__(self, model_name: str = "evo2_7b", local_path: str | None = None):
        """Initialize dummy model with minimal state."""
        self.model_name = model_name
        self.tokenizer = DummyTokenizer(512)
        random.seed(42)

    def forward(
        self,
        input_ids: torch.Tensor,
        return_embeddings: bool = False,
        layer_names: List[str] | None = None,
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor] | None]:
        """Dummy forward pass returning plausible shaped outputs."""
        batch_size, seq_len = input_ids.shape
        vocab_size = self.tokenizer.vocab_size

        logits = torch.randn(batch_size, seq_len, vocab_size)

        if return_embeddings:
            assert layer_names, "layer_names required when return_embeddings=True"
            embeddings = {}
            for layer_name in layer_names:
                embedding_dim = 256
                embeddings[layer_name] = torch.randn(batch_size, seq_len, embedding_dim)
            return logits, embeddings

        return logits, None

    def __call__(
        self,
        input_ids: torch.Tensor,
        return_embeddings: bool = False,
        layer_names: List[str] | None = None,
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor] | None]:
        """Allow calling model as function."""
        return self.forward(input_ids, return_embeddings, layer_names)

    def score_sequences(
        self,
        seqs: List[str],
        batch_size: int = 1,
        prepend_bos: bool = False,
        reduce_method: str = "mean",
        average_reverse_complement: bool = False,
    ) -> List[float]:
        """Return dummy log probability scores for sequences."""
        scores = []
        for seq in seqs:
            seq_len = len(seq)
            if reduce_method == "mean":
                score = -1.5 + (random.random() * 0.5)
            else:
                base_score = -1.5 + (random.random() * 0.5)
                score = base_score * seq_len
            scores.append(score)
        return scores

    def generate(
        self,
        prompt_seqs: List[str],
        n_tokens: int = 500,
        temperature: float = 1.0,
        top_k: int = 4,
        top_p: float = 1.0,
        batched: bool = True,
        cached_generation: bool = True,
        verbose: int = 1,
        force_prompt_threshold: int | None = None,
    ) -> DummyGeneration:
        """Generate dummy DNA sequences based on prompts."""
        nucleotides = ["A", "C", "G", "T"]
        generated_seqs = []

        for _prompt in prompt_seqs:
            actual_n_tokens = min(n_tokens, random.randint(1, n_tokens))
            generated = "".join(random.choices(nucleotides, k=actual_n_tokens))
            generated_seqs.append(generated)

        return DummyGeneration(sequences=generated_seqs)
