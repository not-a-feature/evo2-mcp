# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2025-10-23

### Changed
- Refactored documentation structure and content

## [0.2.0] - 2025-10-20

### Added
- `get_embedding_layers`: New tool to list available layers for embedding extraction from Evo2 checkpoints
- Support for layer discovery and selection guidance for downstream tasks

## [0.1.0] - 2025-10-19

### Added
- Initial release of evo2-mcp
- MCP server implementation for Evo2 genomic sequence operations
- Tools for sequence generation, scoring, and embedding
- `generate_sequence`: Generate genomic sequences using Evo2
- `score_sequence`: Score genomic sequences
- `embed_sequence`: Generate embeddings for genomic sequences
- `score_snp`: SNP variant effect prediction
- Dummy implementation for testing without GPU/model requirements
- Support for Python 3.12 and 3.13
- Test suite with pytest

[Unreleased]: https://github.com/not-a-feature/evo2-mcp/compare/v0.2.2...HEAD
[0.2.2]: https://github.com/not-a-feature/evo2-mcp/compare/v0.2.0...v0.2.2
[0.2.0]: https://github.com/not-a-feature/evo2-mcp/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/not-a-feature/evo2-mcp/releases/tag/v0.1.0
