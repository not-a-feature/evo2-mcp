# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-10-19

### Added
- Initial release of evo2-mcp
- MCP server implementation for Evo2 genomic sequence operations
- Tools for sequence generation, scoring, and embedding
- Dummy implementation for testing without GPU/model requirements
- Comprehensive installation documentation
- Support for Python 3.12, and 3.13
- CI/CD pipelines with GitHub Actions
- Documentation hosted on ReadTheDocs
- Test suite with pytest
- BioContextAI registry integration

### Features
- `generate_sequence`: Generate genomic sequences using Evo2
- `score_sequence`: Score genomic sequences
- `embed_sequence`: Generate embeddings for genomic sequences
- Environment variable `EVO2_MCP_USE_DUMMY` for development mode

### Documentation
- Installation guide with detailed Evo2 dependency setup
- API documentation
- Dummy vs Real implementation comparison
- MCP client configuration examples

[Unreleased]: https://github.com/not-a-feature/evo2-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/not-a-feature/evo2-mcp/releases/tag/v0.1.0
