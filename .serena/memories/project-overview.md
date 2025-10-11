# BP-to-Constitution Project Overview

## Project Purpose

Transform Sequoia Capital pitch decks into executable MVP specifications for AI agents through constitutional principles. Bridges the gap between business vision and technical implementation.

**Core Value**: Business plan → 4 strategic constitutions → 5-10 feature constitutions → AI agents build MVP

## Tech Stack

- **Language**: Python 3.11+
- **CLI Framework**: Typer (matches Speckit)
- **Console UI**: Rich (formatting and tables)
- **Markdown Parsing**: markdown-it-py (CommonMark compliant)
- **Template Rendering**: Jinja2
- **PDF Extraction**: PyMuPDF (for --from-pdf mode)
- **Data Validation**: Pydantic
- **YAML Processing**: PyYAML
- **HTTP Client**: httpx[socks] (for template downloads)
- **Testing**: pytest, pytest-cov

## Code Structure

```
src/bpkit_cli/
├── commands/          # CLI commands (init, clarify, analyze, checklist, decompose)
├── core/             # Business logic (parsers, extractors, validators)
├── models/           # Data models (Pydantic classes)
├── templates/        # Jinja2 templates for constitution generation
└── utils/            # Helper utilities

specs/                # Feature specifications (Speckit format)
├── 001-bp-kit-build/
├── 002-bp-kit-quality/
└── 003-implement-bp-decompose/

tests/                # Test suite
├── unit/
├── integration/
└── fixtures/
```

## Key Commands

### Development
- `ruff check .` - Lint code
- `ruff format .` - Format code
- `pytest` - Run tests
- `pytest --cov` - Run tests with coverage

### CLI Usage
- `bpkit init` - Initialize BP-Kit in project
- `bpkit check` - Validate installation
- `bpkit clarify` - Resolve pitch deck ambiguities
- `bpkit analyze` - Validate constitutional consistency
- `bpkit checklist` - Generate quality checklists
- `bpkit decompose` - Transform pitch deck to constitutions (Feature 003 - in development)

## Project Structure Philosophy

**Single-project structure**: All functionality in one Python package (bpkit-cli)
- CLI tool, not web/mobile app
- Shared core infrastructure (parsers, validators)
- Extends existing package from Feature 002

## Code Style

- **Line length**: 100 characters
- **Type hints**: Required for all function signatures (mypy checked)
- **Docstrings**: Google style for all public functions/classes
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Imports**: Sorted with isort (E, W, F, I, B, C4, UP rules)

## BP-Kit Constitutional Principles

1. **Speckit Architecture Clone**: Use Python + Typer + Rich, install via uv
2. **Business-to-Code Bridge**: 4 strategic + 5-10 feature constitutions
3. **Bidirectional Traceability**: Pitch deck ← constitutions ← features
4. **Speckit Compatibility**: Feature constitutions work with /speckit.plan
5. **AI-Executable**: Constitutions complete enough for agents to implement

## Active Features

- **Feature 001**: BP-Kit Build - Core CLI infrastructure, init command
- **Feature 002**: Quality Commands - clarify, analyze, checklist (COMPLETED)
- **Feature 003**: Decompose Command - Pitch deck → constitutions (IN PROGRESS)

## Success Criteria (Feature 003)

- SC-001: Decomposition in <2 minutes
- SC-004: 70%+ principle extraction accuracy
- SC-012: AirBnB end-to-end test passes
