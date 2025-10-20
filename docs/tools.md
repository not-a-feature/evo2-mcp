# Evo 2 MCP Tools

The evo2-mcp server exposes Evo 2 as a Model Context Protocol (MCP) server, providing tools for genomic sequence analysis. Any MCP-compatible client can use these tools to score, embed, and generate DNA sequences.

## Available Tools

### Sequence Scoring

```{autofunction} evo2_mcp.tools.score_sequence
```

Evaluate DNA sequence likelihood under the Evo 2 model for genome quality assessment or variant comparison.

### Sequence Embedding

```{autofunction} evo2_mcp.tools.embed_sequence
```

Extract learned feature representations from intermediate model layers for downstream analysis, similarity search, or machine learning pipelines.

### Embedding Layer Selection

```{autofunction} evo2_mcp.tools.get_embedding_layers
```

List available layers for embedding extraction from a specific checkpoint to help select the most appropriate layer for your analysis task.

### Sequence Generation

```{autofunction} evo2_mcp.tools.generate_sequence
```

Generate novel DNA sequences conditioned on a prompt for synthetic biology, sequence design, or data augmentation.

### SNP Variant Effect Prediction

```{autofunction} evo2_mcp.tools.score_snp
```

Score the effect of single-nucleotide polymorphisms (SNPs) on sequence likelihood for variant prioritization and interpretation.

## Checkpoint Selection

```{autofunction} evo2_mcp.tools.list_available_checkpoints
```

Select the appropriate checkpoint based on your constraints and use case:

| Checkpoint | Size | Context | Use Case |
|-----------|------|---------|----------|
| evo2_7b | 7B | 1M | General genomic analysis |
| evo2_40b | 40B | 1M | Complex analyses (multi-GPU) |
| evo2_7b_base | 7B | 8K | General-purpose base model |
| evo2_40b_base | 40B | 8K | Base model for large-scale tasks |
| evo2_1b_base | 1B | 8K | Fast inference |

Note
----
The following Evo 2 checkpoints are currently not supported by the official
Evo 2 package and therefore not included here: `evo2_7b_262k`, `evo2_7b_microviridae`.
They will be added to this documentation once official support is available.

## Parameters

### Common Parameters

- **sequence/prompt**: DNA sequences using IUPAC nucleotides (A, C, G, T)
- **checkpoint**: Model checkpoint identifier (optional, defaults to evo2_7b)
- **reduce_method**: Aggregation method for scoring: "mean" or "sum"

### Generation Parameters

- **n_tokens**: Number of tokens to generate (default: 400)
- **temperature**: Sampling temperature; lower values (0.5-0.8) are more deterministic, higher values (1.0+) explore more diversity
- **top_k**: Nucleus sampling; typical value is 4

### Embedding Parameters

- **layer_name**: Model layer to extract from (default: "blocks.2.mlp.l3")
