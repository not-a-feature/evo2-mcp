"""Evo 2 model tools for MCP server.

This module provides a collection of MCP tools for interacting with the Evo 2
language model for genomic sequence analysis. The tools enable scoring, embedding,
generating, and variant effect prediction for DNA sequences.

We import the implementation module to trigger tool registration with the MCP
server via decorators. For documentation and direct imports, we then expose
plain callables that wrap the underlying functions. This ensures Sphinx can
extract proper signatures and docstrings.
"""

from __future__ import annotations

from . import _evo2 as _impl  # Import module to trigger @mcp.tool registration side-effects


def _unwrap(name: str):
    obj = getattr(_impl, name)
    assert hasattr(obj, "fn"), f"Tool '{name}' does not expose an underlying function via .fn"
    return obj.fn  # plain callable used for docs and direct imports


# Public API: expose plain callables with original signatures/docstrings
score_sequence = _unwrap("score_sequence")
embed_sequence = _unwrap("embed_sequence")
generate_sequence = _unwrap("generate_sequence")
score_snp = _unwrap("score_snp")
list_available_checkpoints = _unwrap("list_available_checkpoints")
get_embedding_layers = _unwrap("get_embedding_layers")

__all__ = [
    "embed_sequence",
    "generate_sequence",
    "get_embedding_layers",
    "list_available_checkpoints",
    "score_sequence",
    "score_snp",
]
