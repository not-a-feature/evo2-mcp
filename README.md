# evo2-mcp

![evo2-mcp banner](https://raw.githubusercontent.com/not-a-feature/evo2-mcp/main/docs/_static/evo2-mcp.png)

[![BioContextAI - Registry](https://img.shields.io/badge/Registry-package?style=flat&label=BioContextAI&labelColor=%23fff&color=%233555a1&link=https%3A%2F%2Fbiocontext.ai%2Fregistry)](https://biocontext.ai/registry/not-a-feature/evo2-mcp)
[![Tests][badge-tests]][tests]
[![Documentation][badge-docs]][documentation]

[badge-tests]: https://img.shields.io/github/actions/workflow/status/not-a-feature/evo2-mcp/test.yaml?branch=main
[badge-docs]: https://img.shields.io/readthedocs/evo2-mcp

The evo2-mcp server exposes [Evo 2](https://github.com/ArcInstitute/evo2) as a Model Context Protocol (MCP) server, providing tools for genomic sequence analysis. Any MCP-compatible client can use these tools to score, embed, and generate DNA sequences.

## Features

- **Sequence Scoring**: Compute log probabilities for DNA sequences
- **Sequence Embedding**: Extract learned representations from intermediate model layers
- **Sequence Generation**: Generate novel DNA sequences with controlled sampling
- **Variant Effect Prediction**: Score SNP mutations for variant prioritization
- **Multiple Model Checkpoints**: Support for 7B, 40B, and 1B parameter models

## Getting Started

**Prerequisites**: Python 3.12 or newer

1. **Install Evo2 dependencies**: See [Installation Guide][installation] for details.
   ```bash
   conda install -c nvidia cuda-nvcc cuda-cudart-dev
   conda install -c conda-forge transformer-engine-torch=2.3.0
   pip install flash-attn==2.8.0.post2 --no-build-isolation
   pip install evo2
   ```

2. **Install evo2-mcp**:
   ```bash
   pip install evo2-mcp
   ```

3. **Activate MCP Server**:
   Add the following to your `mcp.json` configuration:

   ```json
   {
   "mcpServers": {
      "evo2-mcp": {
         "command": "python",
         "args": ["-m", "evo2_mcp.main"]
      }
   }
   }
   ```

For detailed installation instructions, see the [Installation Guide][installation].

## Usage

Once installed, the server can be accessed by any MCP-compatible client. For available tools and usage examples, see the [Tools Documentation][tools].

### Available Tools

- `score_sequence` - Evaluate DNA sequence likelihood
- `embed_sequence` - Extract feature representations
- `generate_sequence` - Generate novel DNA sequences
- `score_snp` - Predict variant effects
- `get_embedding_layers` - List available embedding layers
- `list_available_checkpoints` - Show supported model checkpoints

See the [Tools Documentation][tools] for detailed API reference and examples.

## Documentation

- **[Installation Guide][installation]** - Detailed installation instructions
- **[Tools Reference][tools]** - Complete API documentation and usage examples
- **[Development Guide][development]** - Contributing and testing information
- **[Changelog][changelog]** - Version history and updates

You can also find this project on [BioContextAI](https://biocontext.ai/registry/not-a-feature/evo2-mcp), the community hub for biomedical MCP servers.

## Citation

If you use evo2-mcp in your research, please cite:

```bibtex
@software{evo2_mcp,
  author = {Kreuer, Jules},
  title = {evo2-mcp: MCP server for Evo 2 genomic sequence operations},
  year = {2025},
  url = {https://github.com/not-a-feature/evo2-mcp},
  version = {0.2.2}
}
```

For the underlying Evo 2 model, please also cite the original Evo 2 publication.

## License and Attribution

The banner image in this repository is a modified version of the original [Evo 2 banner](https://github.com/ArcInstitute/evo2/blob/main/evo2.jpg) from the [Evo 2 project](https://github.com/ArcInstitute/evo2), which is released under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). It was modified using Google Gemini "Nanobana" and GIMP.

[installation]: https://evo2-mcp.readthedocs.io/en/latest/installation.html
[tools]: https://evo2-mcp.readthedocs.io/en/latest/tools.html
[development]: https://evo2-mcp.readthedocs.io/en/latest/development.html
[issue tracker]: https://github.com/not-a-feature/evo2-mcp/issues
[tests]: https://github.com/not-a-feature/evo2-mcp/actions/workflows/test.yaml
[documentation]: https://evo2-mcp.readthedocs.io
[changelog]: https://evo2-mcp.readthedocs.io/en/latest/changelog.html
[pypi]: https://pypi.org/project/evo2-mcp
