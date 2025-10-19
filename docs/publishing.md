# Pre-Publication Checklist

Use this checklist before publishing a new release to PyPI.

## ✅ Completed Items

- [x] Fix typo in package description ("scoreing" → "scoring")
- [x] Add comprehensive installation guide
- [x] Create CHANGELOG.md
- [x] Add proper citation information
- [x] Add PyPI keywords for discoverability
- [x] Add comprehensive classifiers (license, audience, topics)
- [x] Add additional project URLs
- [x] Version bumped to 0.1.0

## 🔍 Pre-Release Verification

Before creating a release, verify the following:

### 1. Version Number
- [ ] Update version in `pyproject.toml`
- [ ] Update version in `CHANGELOG.md`
- [ ] Version follows semantic versioning (MAJOR.MINOR.PATCH)

### 2. Documentation
- [ ] All documentation builds without errors: `uv run hatch run docs:build`
- [ ] README.md is up to date
- [ ] CHANGELOG.md has entry for this version
- [ ] API documentation is current
- [ ] Installation guide reflects any new requirements

### 3. Code Quality
- [ ] All tests pass: `pytest`
- [ ] Tests pass with dummy implementation: `EVO2_MCP_USE_DUMMY=true pytest`
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`
- [ ] No TODO or FIXME comments in production code

### 4. Build Testing
- [ ] Package builds successfully: `uv build`
- [ ] Check build artifacts in `dist/`
- [ ] Verify wheel contains all necessary files
- [ ] Test installation in clean virtual environment:
  ```bash
  python -m venv test_env
  test_env/Scripts/activate  # Windows
  pip install dist/evo2_mcp-*.whl
  evo2_mcp --help
  ```

### 5. Dependencies
- [ ] All dependencies have appropriate version constraints
- [ ] Optional dependencies are properly categorized
- [ ] No unnecessary dependencies included
- [ ] Installation instructions match actual requirements

### 6. Metadata
- [ ] Author/maintainer information is correct
- [ ] License is correct (LGPL-3.0)
- [ ] Keywords are relevant and complete
- [ ] Classifiers accurately describe the package
- [ ] All URLs are valid and accessible

### 7. GitHub Repository
- [ ] All code is committed and pushed
- [ ] Branch protection rules are configured
- [ ] CI/CD workflows are passing
- [ ] Issue templates are in place
- [ ] README displays correctly on GitHub

### 8. Release Process
- [ ] Create git tag: `git tag -a v0.1.0 -m "Release version 0.1.0"`
- [ ] Push tag: `git push origin v0.1.0`
- [ ] Create GitHub Release with release notes
- [ ] GitHub Actions will automatically publish to PyPI (trusted publishing)

### 9. Post-Release
- [ ] Verify package appears on PyPI: https://pypi.org/project/evo2_mcp/
- [ ] Test installation from PyPI: `pip install evo2_mcp`
- [ ] Verify documentation updated on ReadTheDocs
- [ ] Update BioContextAI registry if needed
- [ ] Announce release (if applicable)

## 📝 Release Notes Template

When creating a GitHub Release, use this template:

```markdown
## evo2-mcp v0.1.0

### 🎉 Highlights
- Brief description of major features/changes

### ✨ New Features
- Feature 1
- Feature 2

### 🐛 Bug Fixes
- Fix 1
- Fix 2

### 📚 Documentation
- Documentation improvements

### 🔧 Maintenance
- Dependency updates
- Infrastructure improvements

### 📦 Installation

**Important**: Evo2 dependencies must be installed first:

\`\`\`bash
# Install CUDA dependencies
conda install -c nvidia cuda-nvcc cuda-cudart-dev
conda install -c conda-forge transformer-engine-torch=2.3.0
pip install flash-attn==2.8.0.post2 --no-build-isolation

# Install Evo2
pip install evo2

# Install evo2-mcp
pip install evo2_mcp==0.1.0
\`\`\`

See the [installation guide](https://evo2-mcp.readthedocs.io/en/latest/installation.html) for details.

### 🔗 Links
- [Documentation](https://evo2-mcp.readthedocs.io/)
- [Changelog](https://evo2-mcp.readthedocs.io/en/latest/changelog.html)
- [PyPI](https://pypi.org/project/evo2_mcp/)
```

## 🚨 Common Issues

### Build fails
- Ensure `hatchling` is installed: `pip install hatchling`
- Check that all required files are present
- Verify `pyproject.toml` syntax is correct

### Tests fail
- Ensure test dependencies are installed: `pip install -e ".[test]"`
- Check that `EVO2_MCP_USE_DUMMY=true` is set if Evo2 is not installed
- Verify Python version is 3.12+

### Import errors after installation
- Check that `src/evo2_mcp/__init__.py` exists
- Verify package structure in wheel: `unzip -l dist/*.whl`
- Ensure `hatch.build.targets.wheel.packages` is correct in `pyproject.toml`

### PyPI upload fails
- Verify GitHub Actions has proper permissions
- Check that PyPI trusted publishing is configured
- Ensure version number hasn't been used before
