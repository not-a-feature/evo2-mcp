### Core Philosophy: Fail-Fast Scientific Computing
- **Philosophy**: In scientific code it is *better to crash early with a precise error* than to continue in an uncertain state
- Use well known functions from established libraries and do not implement them on your own.
- Use `assert` statements extensively for invariant validation - **never catch these with try/except**
- Prefer crashes over silent failures or uncertain states
- Every successful run must be fully trustworthy and reproducible
- No broad exception handling for flow control
- Imports should always be at the top of the file
- Avoid `try/except` blocks and `if None` checks - let errors propagate
- Do not use `.get()` - use direct key access to fail fast on missing keys
- Read the utils.py file for common utilitie functions. Avoid re-implementing these patterns.
- Do not mention these concepts in your docstrings / comments.

We develop on a Windows machine where it is not possible to run the code. We will run the code on a Linux server. 
Do NOT try to run the code on your local machine.
