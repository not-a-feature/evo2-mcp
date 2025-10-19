# Installation Guide

## Prerequisites

- **Python 3.12 or newer**
- **Conda** (recommended for managing CUDA dependencies)
- **NVIDIA GPU** with CUDA support (required for Evo2)

## Step-by-Step Installation

### 1. Install Evo2 Dependencies

Evo2 requires specific CUDA and deep learning dependencies that must be installed in a particular order. **This order is critical for proper functionality.**

#### Step 1.1: Install CUDA Dependencies

Using conda, install the NVIDIA CUDA toolkit components:

```bash
conda install -c nvidia cuda-nvcc cuda-cudart-dev
```

#### Step 1.2: Install Transformer Engine

Install the transformer engine for PyTorch:

```bash
conda install -c conda-forge transformer-engine-torch=2.3.0
```

#### Step 1.3: Install Flash Attention

Install flash-attn with the `--no-build-isolation` flag:

```bash
pip install flash-attn==2.8.0.post2 --no-build-isolation
```

**Note**: The `--no-build-isolation` flag is important for compatibility with the previously installed CUDA components.

#### Step 1.4: Install Evo2

Finally, install the Evo2 package:

```bash
pip install evo2
```

### 2. Install evo2-mcp

After completing all Evo2 dependencies, you can install the MCP server using one of the following methods:

#### Option A: Using uvx (Recommended)

Run directly without installation:

```bash
uvx evo2_mcp
```

#### Option B: Using pip

Install as a package:

```bash
pip install evo2_mcp
```

#### Option C: Install from Source

For development or latest changes:

```bash
pip install git+https://github.com/not-a-feature/evo2-mcp.git@main
```

### 3. MCP Client Configuration

To use this server with an MCP client, add the following to your `mcp.json` configuration:

```json
{
  "mcpServers": {
    "evo2-mcp": {
      "command": "uvx",
      "args": ["evo2_mcp"],
      "env": {
        "UV_PYTHON": "3.12"
      }
    }
  }
}
```

Or if you installed via pip:

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

## Troubleshooting

### CUDA-related Errors

If you encounter CUDA-related errors:

1. Verify your NVIDIA GPU and driver are properly installed:
   ```bash
   nvidia-smi
   ```

2. Ensure CUDA toolkit is accessible:
   ```bash
   nvcc --version
   ```

3. Check that PyTorch detects CUDA:
   ```python
   import torch
   print(torch.cuda.is_available())
   ```

### Installation Order Issues

If Evo2 fails to import or run:

1. Uninstall all related packages:
   ```bash
   pip uninstall evo2 flash-attn transformer-engine-torch -y
   conda remove cuda-nvcc cuda-cudart-dev transformer-engine-torch -y
   ```

2. Follow the installation steps again in the exact order specified above.

### Memory Issues

Evo2 models are large and require significant GPU memory. If you encounter out-of-memory errors:

- Ensure you have a GPU with at least 16GB VRAM (24GB+ recommended)
- Close other GPU-intensive applications
- Consider using the dummy implementation for testing (see Development section)

## Development Installation (Without Evo2)

For testing and development without requiring the full Evo2 installation, you can use the dummy implementation:

```bash
# Set environment variable to use dummy implementation
export EVO2_MCP_USE_DUMMY=true  # Linux/macOS
set EVO2_MCP_USE_DUMMY=true     # Windows (cmd)
$env:EVO2_MCP_USE_DUMMY="true"  # Windows (PowerShell)

# Install only the MCP server
pip install evo2_mcp
```

This is useful for:
- CI/CD pipelines
- Development without GPU access
- Testing MCP integration without model dependencies

## Verifying Installation

After installation, verify everything works:

```python
# Test Evo2 import
import evo2

# Test MCP server
from evo2_mcp import mcp

print("Installation successful!")
```

Or run the test suite:

```bash
# With real Evo2
pytest -m real_evo2

# With dummy implementation
EVO2_MCP_USE_DUMMY=true pytest
```
