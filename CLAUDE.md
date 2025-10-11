# bp-to-constitution Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-10-10

## Active Technologies
- Python 3.11+ + Typer (CLI framework), Rich (console UI), httpx[socks] (HTTP client for downloads), platformdirs (user config directories), pydantic (data validation), pyyaml (YAML parsing) (001-bp-kit-build)
- Python 3.11+ (matches Speckit and existing BP-Kit codebase) (003-implement-bp-decompose)
- Filesystem-based (markdown files in `.specify/` directory structure) (003-implement-bp-decompose)

## Project Structure
```
src/
tests/
```

## Commands
cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style
Python 3.11+: Follow standard conventions

## Recent Changes
- 003-implement-bp-decompose: Added Python 3.11+ (matches Speckit and existing BP-Kit codebase)
- 002-bp-kit-quality: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
- 001-bp-kit-build: Added Python 3.11+ + Typer (CLI framework), Rich (console UI), httpx[socks] (HTTP client for downloads), platformdirs (user config directories), pydantic (data validation), pyyaml (YAML parsing)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
