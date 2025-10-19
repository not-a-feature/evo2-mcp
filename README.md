# evo2-mcp

<a href="https://biocontext.ai/registry/not-a-feature/evo2-mcp">![BioContext][badge-biocontext]</a>
[![Tests][badge-tests]][tests]
[![Documentation][badge-docs]][documentation]

[badge-biocontext]: docs/biocontext.svg
[badge-tests]: https://img.shields.io/github/actions/workflow/status/not-a-feature/evo2-mcp/test.yaml?branch=main
[badge-docs]: https://img.shields.io/readthedocs/evo2-mcp

MCP server for generating, scoreing and embedding genomic sequences using Evo 2

## Getting started

Please refer to the [documentation][],
in particular, the [API documentation][].

You can also find the project on [BioContextAI](https://biocontext.ai), the community-hub for biomedical MCP servers: [evo2-mcp on BioContextAI](https://biocontext.ai/registry/not-a-feature/evo2-mcp).

## Installation

### Prerequisites

You need to have Python 3.12 or newer installed on your system.
If you don't have Python installed, we recommend installing [uv][].

### Installing Evo2 Dependencies (Required)

**Important**: Evo2 has specific installation requirements that must be completed **before** installing this MCP server. Follow these steps in order:

1. **Install CUDA dependencies** (using conda):
   ```bash
   conda install -c nvidia cuda-nvcc cuda-cudart-dev
   conda install -c conda-forge transformer-engine-torch=2.3.0
   ```

2. **Install flash-attn**:
   ```bash
   pip install flash-attn==2.8.0.post2 --no-build-isolation
   ```

3. **Install evo2**:
   ```bash
   pip install evo2
   ```

This installation order is **strongly recommended** to ensure all dependencies are properly configured.

### Installing evo2-mcp

Once Evo2 is installed, there are several options to install evo2-mcp:

1. Use `uvx` to run it immediately:

```bash
uvx evo2_mcp
```

2. Include it in one of various clients that supports the `mcp.json` standard, please use:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "uvx",
      "args": ["evo2_mcp"],
      "env": {
        "UV_PYTHON": "3.12"
      }
    }
  }
}
```

3. Install it through `pip`:

```bash
pip install --user evo2_mcp
```

4. Install the latest development version:

```bash
pip install git+https://github.com/not-a-feature/evo2-mcp.git@main
```

## Development and Testing

### Using the Dummy Implementation

For testing and development without requiring the full Evo2 model dependencies, you can use a dummy implementation that mimics the Evo2 interface:

```bash
export EVO2_MCP_USE_DUMMY=true  # On Linux/macOS
# or
set EVO2_MCP_USE_DUMMY=true     # On Windows (cmd)
# or
$env:EVO2_MCP_USE_DUMMY="true"  # On Windows (PowerShell)
```

This is automatically enabled in GitHub Actions CI/CD pipelines to speed up testing without requiring access to actual model weights.

The dummy implementation:
- Returns realistic output shapes and types
- Generates plausible random values for scores and embeddings
- Does not require downloading or loading any model weights
- Is deterministic (uses fixed random seed) for reproducible tests

### Running Tests

To run tests with the dummy implementation:

```bash
EVO2_MCP_USE_DUMMY=true pytest
```

To run tests with the real Evo2 model (requires model installation):

```bash
pytest -m real_evo2
```

## Contact

If you found a bug, please use the [issue tracker][].

## Citation

If you use evo2-mcp in your research, please cite:

```bibtex
@software{evo2_mcp,
  author = {Kreuer, Jules},
  title = {evo2-mcp: MCP server for Evo 2 genomic sequence operations},
  year = {2025},
  url = {https://github.com/not-a-feature/evo2-mcp},
  version = {0.1.0}
}
```

For the underlying Evo 2 model, please also cite the original Evo 2 publication.

[uv]: https://github.com/astral-sh/uv
[issue tracker]: https://github.com/not-a-feature/evo2-mcp/issues
[tests]: https://github.com/not-a-feature/evo2-mcp/actions/workflows/test.yaml
[documentation]: https://evo2-mcp.readthedocs.io
[changelog]: https://evo2-mcp.readthedocs.io/en/latest/changelog.html
[api documentation]: https://evo2-mcp.readthedocs.io/en/latest/api.html
[pypi]: https://pypi.org/project/evo2-mcp
