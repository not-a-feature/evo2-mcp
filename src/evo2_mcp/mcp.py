"""FastMCP server instance configuration."""

from fastmcp import FastMCP

mcp: FastMCP = FastMCP(
    name="evo2-mcp",
    instructions=(
        "Tools for scoring, embedding, and generating genomic DNA sequences with the Evo 2 foundation model."
    ),
    on_duplicate_tools="error",
)
