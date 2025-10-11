# Implementation Plan: BP-Kit Init Command

**Branch**: `001-bp-kit-build` | **Date**: 2025-10-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-bp-kit-build/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build the `bpkit init` command that installs BP-Kit templates and directory structure into Speckit projects. The command downloads templates from GitHub/CDN, creates required directories (`.specify/deck/`, `.specify/features/`, `.specify/changelog/`, `.specify/scripts/bp/`), installs slash commands, and handles edge cases like existing installations and missing Git repositories. Technical approach uses Python 3.11+ with Typer CLI framework and httpx for template downloads, following Speckit's exact architecture pattern.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Typer (CLI framework), Rich (console UI), httpx[socks] (HTTP client for downloads), platformdirs (user config directories), pydantic (data validation), pyyaml (YAML parsing)
**Storage**: File system only - templates/scripts/directories created in `.specify/` and `.claude/` folders
**Testing**: pytest with pytest-cov for unit/integration tests
**Target Platform**: Linux, macOS, Windows (cross-platform via Python)
**Project Type**: Single CLI package (installable via `uv tool install`)
**Performance Goals**: Complete `bpkit init` in <30 seconds including template downloads (SC-001)
**Constraints**: Network-dependent (templates downloaded from GitHub/CDN), requires write permissions to target directory, 95% first-try success rate (SC-003)
**Scale/Scope**: Small-scale CLI tool - 3 templates, 2 slash commands, 2 bash scripts, 4 directories to create (12 files total per SC-006)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Speckit Architecture Clone (NON-NEGOTIABLE)

**Requirement**: BP-Kit MUST mirror Speckit's exact structure to ensure seamless integration and familiar developer experience.

**Evidence**:
- ✅ **Python 3.11+ with Typer + Rich**: Technical Context confirms Python 3.11+, Typer CLI, Rich console UI (matches Speckit)
- ✅ **uv tool install method**: FR-010 specifies `uvx --from git+https://...` installation method
- ✅ **Command-based workflow**: `bpkit init`, `bpkit check` commands defined
- ✅ **Templates in `.specify/`**: FR-001, FR-002 create templates in `.specify/templates/`
- ✅ **Slash commands in `.claude/commands/`**: FR-003 creates `bp.decompose.md`, `bp.sync.md`

**Status**: ✅ PASS - Architecture perfectly mirrors Speckit

### Principle II: Business-to-Code Bridge

**Requirement**: Transform Sequoia-format pitch decks into two levels of executable constitutions that AI agents can implement.

**Evidence**:
- ✅ **Level 1 (Strategic)**: FR-002 installs `strategic-constitution-template.md`
- ✅ **Level 2 (Feature)**: FR-002 installs `feature-constitution-template.md`
- ✅ **Pitch deck template**: FR-002 installs `pitch-deck-template.md` (Sequoia format)

**Status**: ✅ PASS - Templates enable decomposition workflow

### Principle III: Bidirectional Traceability (NON-NEGOTIABLE)

**Requirement**: Every constitutional principle MUST link to its source. Changes flow in both directions.

**Evidence**:
- ✅ **Changelog directory**: FR-001 creates `.specify/changelog/` for tracking changes
- ✅ **Link structure**: Templates include traceability links (from existing templates)
- ⚠️ **Sync mechanism**: `/bp.sync` command planned but not implemented in this feature (out of scope for init)

**Status**: ✅ PASS - Init creates infrastructure for traceability; sync is separate feature

### Principle IV: Speckit Compatibility

**Requirement**: BP-Kit's output (feature constitutions) MUST be valid input to Speckit's workflow.

**Evidence**:
- ✅ **Compatible directory structure**: FR-001 creates `.specify/features/` where Speckit looks for constitutions
- ✅ **No conflicts**: FR-006 validates no overwrites of Speckit files (`/speckit.*` commands, Speckit templates)
- ✅ **Coexistence**: Clarification confirms `.specify/` directory detection for existing Speckit projects

**Status**: ✅ PASS - Zero conflicts with Speckit (SC-002)

### Principle V: AI-Executable Specifications

**Requirement**: Feature constitutions MUST be complete enough for AI agents to build MVPs without human clarification.

**Evidence**:
- ✅ **Complete templates**: FR-002 installs templates with user stories, data models, principles, success criteria
- ✅ **Slash commands ready**: FR-003 creates `/bp.decompose` and `/bp.sync` for AI agent workflows
- ✅ **Bash utilities**: FR-004 creates helper scripts in `.specify/scripts/bp/`

**Status**: ✅ PASS - Templates installed are AI-executable

**Overall Constitution Check**: ✅ **PASS** - All 5 principles satisfied

## Project Structure

### Documentation (this feature)

```
specs/001-bp-kit-build/
├── spec.md              # Feature specification
├── checklists/
│   └── requirements.md  # Requirements validation checklist
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (template download patterns, CLI best practices)
├── data-model.md        # Phase 1 output (Template, InstallationState entities)
├── quickstart.md        # Phase 1 output (How to use bpkit init)
└── contracts/           # Phase 1 output (Template download API specs)
```

### Source Code (repository root)

```
# Single project structure (CLI tool)
src/bpkit_cli/
├── __init__.py          # Main CLI entry point with Typer app (already exists)
├── commands/
│   ├── __init__.py
│   ├── init.py          # bpkit init command implementation
│   └── check.py         # bpkit check command implementation (already exists)
├── core/
│   ├── __init__.py
│   ├── templates.py     # Template download and management
│   ├── installer.py     # Directory creation, file writing, rollback logic
│   └── validation.py    # Speckit detection, conflict checking
└── models/
    ├── __init__.py
    ├── template.py      # Template entity (name, source URL, content)
    └── install_state.py # Installation state tracking

tests/
├── conftest.py          # Pytest fixtures (temp directories, mock httpx)
├── unit/
│   ├── test_templates.py
│   ├── test_installer.py
│   └── test_validation.py
├── integration/
│   ├── test_init_fresh.py        # Test P2: Bootstrap new project
│   ├── test_init_existing.py     # Test P1: Install in Speckit project
│   └── test_init_overwrite.py    # Test overwrite prompt behavior
└── contract/
    └── test_template_downloads.py # Verify template download contracts

# Template sources (bundled in package or referenced URLs)
src/bpkit_cli/templates/
├── pitch-deck-template.md
├── strategic-constitution-template.md
├── feature-constitution-template.md
├── bp.decompose.md
├── bp.sync.md
├── bp-common.sh
└── decompose-setup.sh
```

**Structure Decision**: Single CLI project structure chosen because:
- BP-Kit is a standalone command-line tool (not web/mobile)
- No frontend/backend separation needed
- Installable as single Python package via `uv tool install`
- Follows Speckit's exact structure (single `src/specify_cli/` layout)

## Complexity Tracking

*No violations to justify - all constitution principles satisfied.*

## Phase 0: Research & Unknowns

**Research areas to explore**:

1. **Template Download Patterns**
   - Decision needed: Use httpx async vs sync for template downloads
   - Best practices for retry logic (network failures)
   - Cache strategy (should downloaded templates be cached?)
   - GitHub raw URL patterns vs GitHub API vs CDN

2. **Rollback Implementation**
   - Python context manager for atomic operations
   - Safe directory/file deletion (avoid deleting user data)
   - Rollback ordering (LIFO: last created, first deleted)

3. **CLI Prompting with Typer + Rich**
   - How to implement Y/N prompts with Typer (use `typer.confirm()` or Rich Prompt?)
   - Handling Ctrl+C gracefully during prompts
   - --force flag to skip all prompts

4. **Speckit Detection Logic**
   - Verify assumption: `.specify/` folder existence = Speckit project
   - Should we check for specific Speckit files to avoid false positives?
   - Edge case: `.specify/` exists but is empty (clarification says "treat as fresh install")

5. **Template Placeholder Replacement**
   - FR-007 requires `--project-name` option to replace `[PROJECT_NAME]` in templates
   - Best approach: string replacement, Jinja2, or custom template engine?
   - Performance consideration: All templates small (< 10KB), simple string replacement sufficient

**Output**: `research.md` documenting decisions for each area above

## Phase 1: Design & Contracts

**Artifacts to generate**:

1. **data-model.md**
   - **Template** entity: name, source_url, destination_path, content, version
   - **InstallationState** entity: installed (bool), files_created (list), conflicts (list)
   - **Directory** entity: path, exists_before_install (for rollback)
   - State transitions: Uninstalled → Installing → Installed → Failed (rollback)

2. **contracts/**
   - `template-download-api.yaml`: OpenAPI spec for GitHub raw content API
   - Expected responses: 200 (success), 404 (not found), 429 (rate limit), 503 (network error)
   - Retry policy: 3 attempts with exponential backoff

3. **quickstart.md**
   - How to install BP-Kit: `uv tool install bpkit-cli --from git+https://...`
   - Usage examples: `bpkit init`, `bpkit init my-project`, `bpkit init --force`
   - Troubleshooting: Network errors, permission issues, Git not detected

4. **Agent context update**
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
   - Add new technology from this plan to Claude's context

## Constitution Check (Post-Design Re-evaluation)

*Re-checked after Phase 1 design completion*

**Status**: ✅ **ALL PRINCIPLES STILL SATISFIED**

**Evidence from Design Artifacts**:

### Principle I: Speckit Architecture Clone ✅
- research.md confirms Python 3.11+, Typer, Rich, httpx (matching Speckit exactly)
- data-model.md entities follow Speckit patterns (Template, InstallationState)
- Project structure: `src/bpkit_cli/` mirrors `src/specify_cli/`
- quickstart.md demonstrates `uv tool install` method (identical to Speckit)

### Principle II: Business-to-Code Bridge ✅
- data-model.md Template entity includes all decomposition types (pitch-deck, strategic, feature)
- contracts/github-raw-api.yaml lists all 7 templates for Level 1 + Level 2 system
- quickstart.md workflow: pitch deck → /bp.decompose → constitutions → Speckit

### Principle III: Bidirectional Traceability ✅
- data-model.md includes `.specify/changelog/` directory for tracking changes
- quickstart.md documents `/bp.sync --to-deck` reverse flow
- Templates maintain traceability links (per spec)

### Principle IV: Speckit Compatibility ✅
- data-model.md InstallationState.conflicts validates FR-006 (no Speckit overwrites)
- CLI contract explicitly lists "Files Never Modified: Any existing Speckit files"
- research.md Speckit detection uses simple `.specify/` check (reliable, no false positives)

### Principle V: AI-Executable Specifications ✅
- data-model.md Template entity has all metadata AI agents need
- contracts/cli-interface.md provides complete executable contract
- quickstart.md gives AI agents clear workflow to follow
- Slash commands (bp.decompose, bp.sync) ready for agent execution

**Design Risks Assessment**:
- Rollback mechanism: Context manager pattern (standard Python practice) ✅
- Template downloads: 3 retries with exponential backoff (industry standard) ✅
- Placeholder replacement: Validated input, simple string replacement (secure) ✅
- Performance: 3-8s typical, 30s max (well within SC-001 target) ✅

**Conclusion**: Design strengthens constitutional compliance. No violations introduced. Ready for task breakdown.

---

## Phase 2: Task Breakdown

*Phase 2 (tasks.md generation) is handled by the `/speckit.tasks` command - NOT part of `/speckit.plan`.*

**Next step**: After reviewing this plan, run `/speckit.tasks` to generate the task breakdown.
