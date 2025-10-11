# Development Workflow

## Task Completion Checklist

When a task is completed:

1. **Lint**: `ruff check .`
2. **Format**: `ruff format .`
3. **Test**: `pytest` (all tests must pass)
4. **Coverage**: `pytest --cov` (maintain >80% coverage)
5. **Type Check**: `mypy src/` (if configured)

## Testing Strategy

- **Unit tests**: Test individual functions/classes in isolation
- **Integration tests**: Test command workflows end-to-end
- **Fixtures**: Use sample pitch decks in `tests/fixtures/`
- **Contract tests**: Validate outputs against schemas in `specs/*/contracts/`

## Git Workflow

- Feature branches: `NNN-feature-name` (e.g., `003-implement-bp-decompose`)
- Commit messages: Descriptive, reference feature/spec
- No force push to main/master
- Pre-commit hooks enforce linting

## Working with Specs

All features documented in `specs/NNN-feature-name/`:
- `spec.md` - Requirements and acceptance criteria
- `plan.md` - Technical implementation plan
- `research.md` - Technical unknowns resolved
- `data-model.md` - Entity relationships
- `tasks.md` - Implementation task breakdown
- `contracts/` - API/interface definitions

Follow Spec-Kit workflow:
1. `/speckit.specify` - Create spec.md
2. `/speckit.clarify` - Resolve ambiguities
3. `/speckit.plan` - Generate plan.md
4. `/speckit.tasks` - Generate tasks.md
5. `/speckit.implement` - Execute tasks

## System Utilities (NixOS)

Modern CLI tools available:
- `fd` - File finding (not find)
- `rg` - Text search (not grep)
- `bat` - File viewing (not cat)
- `eza` - Directory listing (not ls)
- `jless` - JSON viewing
- `delta` - Git diffs
- `dust` - Disk usage

## Package Management

- Uses `uv` for fast dependency management
- Install: `uv pip install -e .` (editable install)
- Add dependency: Edit `pyproject.toml`, then `uv pip install -e .`
- Tool install: `uv tool install bpkit-cli`
