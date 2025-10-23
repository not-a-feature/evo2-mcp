# Development and Testing

## Using the Dummy Implementation

For testing and development without requiring the full Evo2 model dependencies, you can use a dummy implementation that mimics the Evo2 interface:

```bash
export EVO2_MCP_USE_DUMMY=true  # On Linux/macOS
# or
set EVO2_MCP_USE_DUMMY=true     # On Windows (cmd)
# or
$env:EVO2_MCP_USE_DUMMY="true"  # On Windows (PowerShell)
```

This is automatically enabled in GitHub Actions CI/CD pipelines to speed up testing without requiring access to actual model weights.

## Running Tests

To run tests with the dummy implementation:

```bash
EVO2_MCP_USE_DUMMY=true pytest
```

To run tests with the real Evo2 model (requires model installation):

```bash
pytest -m real_evo2
```

## Development Setup

### Installing from Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/not-a-feature/evo2-mcp.git
cd evo2-mcp
pip install -e ".[dev,test]"
```

### Running Tests Locally

The project uses pytest for testing. To run the full test suite:

```bash
# Run all tests (requires Evo2 installation)
pytest

# Run only fast tests with dummy implementation
EVO2_MCP_USE_DUMMY=true pytest

# Run with coverage
pytest --cov=evo2_mcp --cov-report=html
```

### Code Quality

The project uses pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Building Documentation

Build the documentation locally:

```bash
# Using hatch
hatch run docs:build

# Or directly with sphinx
pip install -e ".[doc]"
sphinx-build -M html docs docs/_build
```

Open the documentation in your browser:

```bash
# Using hatch
hatch run docs:open

# Or manually
# On Windows
start docs/_build/html/index.html
# On macOS
open docs/_build/html/index.html
# On Linux
xdg-open docs/_build/html/index.html
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

For more details, see the [issue tracker](https://github.com/not-a-feature/evo2-mcp/issues).
