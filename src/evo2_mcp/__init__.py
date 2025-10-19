"""MCP server for generating, scoring and embedding genomic sequences using Evo 2."""

from importlib.metadata import version

from evo2_mcp.main import run_app
from evo2_mcp.mcp import mcp

__version__ = version("evo2_mcp")

__all__ = ["mcp", "run_app", "__version__"]


if __name__ == "__main__":
    run_app()
