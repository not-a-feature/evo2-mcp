# Dummy vs Real Evo2 Implementation

This document explains the dummy implementation system used for testing without requiring full Evo2 model dependencies.

## Overview

The project supports two modes of operation:

1. **Real Mode**: Uses the actual Evo2 models (requires `evo2` package installation and model weights)
2. **Dummy Mode**: Uses a lightweight mock implementation that mimics the Evo2 interface

## Switching Modes

### Environment Variable

Set the `EVO2_MCP_USE_DUMMY` environment variable:

```bash
# Linux/macOS
export EVO2_MCP_USE_DUMMY=true

# Windows (cmd)
set EVO2_MCP_USE_DUMMY=true

# Windows (PowerShell)
$env:EVO2_MCP_USE_DUMMY="true"
```

Accepted values: `true`, `1`, `yes` (case-insensitive)

### In Tests

```bash
# Run tests with dummy implementation
EVO2_MCP_USE_DUMMY=true pytest

# Run real model integration tests (requires evo2 package)
pytest -m real_evo2
```

## Dummy Implementation Details

The dummy implementation (`src/evo2_mcp/dummy_evo2.py`) provides:

- **DummyEvo2**: Main model class
  - `forward()`: Returns random logits and embeddings with correct shapes
  - `score_sequences()`: Returns plausible log probability scores
  - `generate()`: Generates random DNA sequences
  
- **DummyTokenizer**: Character-level DNA tokenizer
  - Maps A→0, C→1, G→2, T→3, N→4

### Return Value Characteristics

- **Scores**: Random values between -2.0 and -1.0 (mean) or scaled by sequence length (sum)
- **Embeddings**: Random tensors with dimension 256
- **Generated sequences**: Random DNA strings (A, C, G, T) with length up to `n_tokens`
- **Deterministic**: Uses fixed random seed (42) for reproducibility

## GitHub Actions

The CI/CD pipeline automatically uses dummy mode by setting `EVO2_MCP_USE_DUMMY=true` in the test workflow. This:

- Speeds up test execution significantly
- Eliminates need for model weight downloads
- Reduces compute requirements
- Ensures tests pass without external dependencies

## When to Use Each Mode

### Use Dummy Mode For:
- Unit tests
- CI/CD pipelines
- Development without model access
- Fast iteration cycles
- Testing tool interfaces and validation logic

### Use Real Mode For:
- Integration tests with actual model behavior
- Validating model outputs
- Performance benchmarking
- Production deployments

## Implementation Details

The switch is implemented in `src/evo2_mcp/model.py`:

```python
USE_DUMMY_EVO2 = os.getenv("EVO2_MCP_USE_DUMMY", "false").lower() in ("true", "1", "yes")

def _create_model(checkpoint: str) -> Any:
    if USE_DUMMY_EVO2:
        from evo2_mcp.dummy_evo2 import DummyEvo2
        return DummyEvo2(checkpoint)
    
    from evo2 import Evo2
    return Evo2(checkpoint)
```

This ensures a single, centralized switch point for all model instantiation.
