"""Command-line interface for the evo2-mcp server."""

import enum
import logging
import sys
from typing import Literal

import click

from .tools import *  # noqa: F403 import all tools to register them

Transport = Literal["stdio", "http", "sse", "streamable-http"]


class EnvironmentType(enum.Enum):
    """Server environment mode."""

    PRODUCTION = enum.auto()
    DEVELOPMENT = enum.auto()


@click.command(name="run")
@click.option(
    "-t",
    "--transport",
    "transport",
    type=str,
    help="MCP transport option. Defaults to 'stdio'.",
    default="stdio",
    envvar="MCP_TRANSPORT",
)
@click.option(
    "-p",
    "--port",
    "port",
    type=int,
    help="Port of MCP server. Defaults to '8000'",
    default=8000,
    envvar="MCP_PORT",
    required=False,
)
@click.option(
    "-h",
    "--host",
    "hostname",
    type=str,
    help="Hostname of MCP server. Defaults to '0.0.0.0'",
    default="0.0.0.0",
    envvar="MCP_HOSTNAME",
    required=False,
)
@click.option("-v", "--version", "version", is_flag=True, help="Get version of package.")
@click.option(
    "-e",
    "--env",
    "environment",
    type=click.Choice(EnvironmentType, case_sensitive=False),
    default=EnvironmentType.DEVELOPMENT,
    envvar="MCP_ENVIRONMENT",
    help="MCP server environment. Defaults to 'development'.",
)
def run_app(
    transport: str = "stdio",
    port: int = 8000,
    hostname: str = "0.0.0.0",
    environment: EnvironmentType = EnvironmentType.DEVELOPMENT,
    version: bool = False,
):
    """Run the evo2-mcp server.

    MCP server for generating, scoring and embedding genomic sequences using Evo 2.
    Supports stdio (default) and HTTP transports.
    """
    if version:
        from evo2_mcp import __version__

        click.echo(__version__)
        sys.exit(0)

    logger = logging.getLogger(__name__)

    from evo2_mcp.mcp import mcp

    if environment == EnvironmentType.DEVELOPMENT:
        logger.info("Starting MCP server (DEVELOPMENT mode)")
        transport_typed: Transport = transport  # type: ignore[assignment]
        if transport == "http":
            mcp.run(transport=transport_typed, port=port, host=hostname)
        else:
            mcp.run(transport=transport_typed)
    else:
        raise NotImplementedError("Production mode not yet implemented")


if __name__ == "__main__":
    run_app()
