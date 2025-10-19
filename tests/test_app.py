"""Integration tests for MCP tools."""

import pytest  # type: ignore[import]
from fastmcp import Client

import evo2_mcp


def test_package_has_version():
    """Package exposes version."""
    assert evo2_mcp.__version__ is not None


@pytest.mark.asyncio
async def test_score_sequence_tool():
    async with Client(evo2_mcp.mcp) as client:
        result = await client.call_tool("score_sequence", {"sequence": "ACGT"})

    assert result.data["scores"] == [0.5]
    assert result.data["reduce_method"] == "mean"


@pytest.mark.asyncio
async def test_embed_sequence_tool():
    async with Client(evo2_mcp.mcp) as client:
        result = await client.call_tool("embed_sequence", {"sequence": "ACGT"})

    assert result.data["embedding"] == [0.1, 0.2, 0.3]
    assert result.data["layer_name"] == "blocks.2.mlp.l3"


@pytest.mark.asyncio
async def test_generate_sequence_tool():
    async with Client(evo2_mcp.mcp) as client:
        result = await client.call_tool("generate_sequence", {"prompt": "AC"})

    assert result.data["generated_sequence"] == "AC-mock"


@pytest.mark.asyncio
async def test_list_checkpoints_tool():
    async with Client(evo2_mcp.mcp) as client:
        result = await client.call_tool("list_available_checkpoints", {})

    structured = result.structured_content or {}
    entries = structured.get("result", [])
    names = {entry["name"] for entry in entries}
    assert "evo2_7b" in names
    assert "evo2_1b_base" in names


@pytest.mark.asyncio
async def test_score_snp_tool():
    """Test SNP scoring with valid mutation."""
    async with Client(evo2_mcp.mcp) as client:
        result = await client.call_tool(
            "score_snp", {"sequence": "ACGTACGT", "alternative_allele": "T"}
        )

    data = result.data
    assert data["original_sequence"] == "ACGTACGT"
    assert data["mutated_sequence"] == "ACGTTCGT"
    assert data["center_position"] == 4
    assert data["reference_allele"] == "A"
    assert data["alternative_allele"] == "T"
    assert data["original_score"] == 0.5
    assert data["mutated_score"] == 0.5
    assert data["score_delta"] == 0.0


@pytest.mark.asyncio
async def test_score_snp_tool_with_reduce_method():
    """Test SNP scoring with custom reduce method."""
    async with Client(evo2_mcp.mcp) as client:
        result = await client.call_tool(
            "score_snp", {"sequence": "ACGTACGT", "alternative_allele": "G", "reduce_method": "sum"}
        )

    data = result.data
    assert data["reduce_method"] == "sum"
    assert data["reference_allele"] == "A"
    assert data["alternative_allele"] == "G"


@pytest.mark.asyncio
async def test_score_snp_tool_normalizes_case():
    """Test SNP scoring normalizes input to uppercase."""
    async with Client(evo2_mcp.mcp) as client:
        result = await client.call_tool(
            "score_snp", {"sequence": "acgtacgt", "alternative_allele": "t"}
        )

    data = result.data
    assert data["original_sequence"] == "ACGTACGT"
    assert data["alternative_allele"] == "T"


@pytest.mark.asyncio
async def test_score_snp_tool_rejects_same_allele():
    """Test SNP scoring rejects alternative allele matching center."""
    async with Client(evo2_mcp.mcp) as client:
        with pytest.raises(Exception):
            await client.call_tool("score_snp", {"sequence": "ACGTACGT", "alternative_allele": "A"})


@pytest.mark.asyncio
async def test_score_snp_tool_rejects_short_sequence():
    """Test SNP scoring rejects sequences shorter than 3 nucleotides."""
    async with Client(evo2_mcp.mcp) as client:
        with pytest.raises(Exception):
            await client.call_tool("score_snp", {"sequence": "AC", "alternative_allele": "T"})


@pytest.mark.asyncio
async def test_score_snp_tool_rejects_invalid_allele():
    """Test SNP scoring rejects non-DNA alternative alleles."""
    async with Client(evo2_mcp.mcp) as client:
        with pytest.raises(Exception):
            await client.call_tool("score_snp", {"sequence": "ACGTACGT", "alternative_allele": "X"})


@pytest.mark.asyncio
async def test_score_snp_tool_rejects_multi_char_allele():
    """Test SNP scoring rejects multi-character alternative alleles."""
    async with Client(evo2_mcp.mcp) as client:
        with pytest.raises(Exception):
            await client.call_tool(
                "score_snp", {"sequence": "ACGTACGT", "alternative_allele": "AT"}
            )
