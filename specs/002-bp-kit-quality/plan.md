# Implementation Plan: BP-Kit Quality Commands

**Branch**: `002-bp-kit-quality` | **Date**: 2025-10-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-bp-kit-quality/spec.md`

## Summary

Implement 3 optional quality commands (`/bp.clarify`, `/bp.analyze`, `/bp.checklist`) that mirror Speckit's quality workflow pattern to improve constitution quality at the business strategy layer. These commands enable founders to identify pitch deck ambiguities before decomposition, validate constitutional consistency after generation, and apply structured quality gates before AI implementation.

**Technical Approach** (from research.md):
- Markdown parsing via `markdown-it-py` for link extraction and validation
- Lightweight pattern matching for ambiguity detection (no heavy NLP)
- Jinja2 templates for context-specific checklist generation
- Markdown-based slash commands following Speckit's architecture
- Semantic versioning in YAML frontmatter with changelog integration

## Technical Context

**Language/Version**: Python 3.11+ (matches BP-Kit Init Feature 001)
**Primary Dependencies**: markdown-it-py (CommonMark parsing), jinja2 (template rendering), pyyaml (version tracking), typer (CLI), rich (console UI)
**Storage**: Markdown files (.specify/deck/, .specify/memory/, .specify/features/, .specify/checklists/)
**Testing**: pytest with fixtures for temp directories and mock markdown files
**Target Platform**: Linux/macOS/Windows (Claude Code environment)
**Project Type**: Single Python CLI package extending BP-Kit
**Performance Goals**: `/bp.clarify` <10s, `/bp.analyze` <2s, `/bp.checklist` <5s (per success criteria)
**Constraints**: No network dependencies for analysis/checklist, maximum 5 clarification questions, 100% broken link detection rate
**Scale/Scope**: Handle 4 strategic + 10 feature constitutions (~50KB total markdown), validate 100+ traceability links

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Speckit Architecture Clone ✅ PASS

**Compliance**:
- Python 3.11+ package using Typer + Rich (matches BP-Kit Init)
- Extends existing `bpkit` CLI with no new installation method
- Slash commands in `.claude/commands/bp.*.md` (standard location)
- Templates in `.specify/` directory (coexists with existing templates)

**Validation**: No architectural divergence - extends existing BP-Kit structure.

### II. Business-to-Code Bridge ✅ PASS

**Compliance**:
- Commands operate at constitutional layer (pitch deck → constitutions)
- `/bp.clarify` ensures pitch deck completeness (input quality)
- `/bp.analyze` validates 2-level structure (strategic → feature links)
- `/bp.checklist` enforces quality gates for AI-executable specifications

**Validation**: Commands strengthen the decomposition pipeline without changing it.

### III. Bidirectional Traceability ✅ PASS

**Compliance**:
- `/bp.analyze` validates all traceability links (pitch deck ← constitutions ← features)
- Detects broken references (file + section ID validation)
- Checks version consistency (constitutions reference correct pitch deck version)
- Changelog integration (analysis reports saved to `.specify/changelog/`)

**Validation**: Commands enforce traceability, don't bypass it.

### IV. Speckit Compatibility ✅ PASS

**Compliance**:
- Quality commands run BEFORE `/speckit.plan` (pre-implementation validation)
- Feature constitutions validated by `/bp.checklist` remain Speckit-compatible
- Checklist items include "Ready for /speckit.plan" criterion
- No modifications to constitution format

**Validation**: Commands are pre-flight checks, not format changers.

### V. AI-Executable Specifications ✅ PASS

**Compliance**:
- `/bp.clarify` resolves ambiguities that would require AI clarification
- `/bp.analyze` catches broken links that would confuse AI agents
- `/bp.checklist` validates completeness criteria (user stories, data models, success criteria)
- Quality gates reduce AI clarification requests

**Validation**: Commands improve specification quality for AI consumption.

**Overall Constitution Check**: ✅ **PASSED** - No violations, all principles aligned.

## Project Structure

### Documentation (this feature)

```
specs/002-bp-kit-quality/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output - completed by agent
├── data-model.md        # Phase 1 output - completed
├── quickstart.md        # Phase 1 output - completed
├── contracts/           # Phase 1 output - completed
│   └── slash-commands.yaml  # Command interface contracts
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created yet)
```

### Source Code (repository root)

```
src/bpkit_cli/
├── commands/
│   ├── __init__.py
│   ├── init.py (existing - Feature 001)
│   └── check.py (existing - Feature 001)
│   # NEW for this feature:
│   ├── clarify.py        # /bp.clarify implementation
│   ├── analyze.py        # /bp.analyze implementation
│   └── checklist.py      # /bp.checklist implementation
├── models/
│   ├── __init__.py
│   ├── template.py (existing)
│   # NEW for this feature:
│   ├── pitch_deck.py     # PitchDeck, PitchDeckSection
│   ├── constitution.py   # Constitution, Principle, ConstitutionType
│   ├── traceability.py   # TraceabilityLink, LinkType, LinkValidationResult
│   ├── clarification.py  # ClarificationQuestion, Priority
│   ├── analysis.py       # AnalysisReport, ValidationError/Warning/Info
│   └── checklist.py      # Checklist, ChecklistItem
├── core/
│   ├── __init__.py
│   ├── installer.py (existing)
│   ├── templates.py (existing)
│   ├── validation.py (existing)
│   # NEW for this feature:
│   ├── markdown_parser.py   # Markdown parsing with markdown-it-py
│   ├── link_validator.py    # Link extraction and validation
│   ├── ambiguity_detector.py  # Pattern matching for vague sections
│   ├── conflict_detector.py   # Principle contradiction detection
│   └── version_tracker.py     # Semantic version parsing and comparison
└── templates/
    # NEW for this feature:
    ├── strategic-checklist.j2   # Jinja2 template for strategic constitutions
    └── feature-checklist.j2     # Jinja2 template for feature constitutions

.claude/commands/
# NEW for this feature:
├── bp.clarify.md         # Slash command for clarification
├── bp.analyze.md         # Slash command for analysis
└── bp.checklist.md       # Slash command for checklist generation

tests/
├── unit/
│   # NEW for this feature:
│   ├── test_markdown_parser.py
│   ├── test_link_validator.py
│   ├── test_ambiguity_detector.py
│   ├── test_conflict_detector.py
│   ├── test_version_tracker.py
│   ├── test_pitch_deck_model.py
│   ├── test_constitution_model.py
│   └── test_checklist_model.py
├── integration/
│   # NEW for this feature:
│   ├── test_clarify_command.py
│   ├── test_analyze_command.py
│   └── test_checklist_command.py
└── fixtures/
    # NEW for this feature:
    ├── sample-pitch-deck.md
    ├── sample-strategic-constitution.md
    └── sample-feature-constitution.md
```

**Structure Decision**: Extends existing BP-Kit single-package structure. All new code lives under `src/bpkit_cli/` with clear separation: commands (CLI entry points), models (data entities), core (business logic), templates (Jinja2 templates). Slash commands in standard `.claude/commands/` location.

## Complexity Tracking

*No violations - Constitution Check passed without issues.*

## Phase 0: Research (✅ COMPLETED)

**Research document**: [research.md](./research.md) - completed by agent

**Key Decisions Made**:

1. **Markdown Parsing**: markdown-it-py (CommonMark compliant, AST-based, already transitive dependency via Rich)
2. **Semantic Analysis**: Lightweight pattern matching (no spaCy/NLTK overhead)
3. **Checklist Generation**: Jinja2 templates with context-specific items
4. **Slash Commands**: Markdown files with YAML frontmatter following Speckit pattern
5. **Version Tracking**: Semantic versioning in YAML frontmatter + changelog directory

**Performance Validated**: All operations complete in <500ms for typical projects (well under 10s target).

**Dependencies Added**: Only 3 lightweight packages - markdown-it-py, jinja2, pyyaml (all battle-tested).

## Phase 1: Design (✅ COMPLETED)

### Data Model

**Document**: [data-model.md](./data-model.md) - completed

**Core Entities** (10 total):
1. **PitchDeck** - Represents pitch deck with sections and version
2. **PitchDeckSection** - Individual section (e.g., #problem, #solution)
3. **Constitution** - Strategic or feature constitution document
4. **Principle** - Individual constitutional principle with traceability
5. **TraceabilityLink** - Reference from one document to another
6. **ClarificationQuestion** - Ambiguity requiring user input
7. **AnalysisReport** - Results from `/bp.analyze` validation
8. **ValidationError/Warning/Info** - Specific issues found during analysis
9. **ChecklistItem** - Individual validation criterion
10. **Checklist** - Collection of items for a constitution

**State Machines**:
- TraceabilityLink: CREATED → VALID/BROKEN_FILE/BROKEN_SECTION/MISSING_SOURCE
- ClarificationQuestion: CREATED → ANSWERED → APPLIED
- Checklist: EMPTY → INCOMPLETE → COMPLETE

**Relationships**:
- PitchDeck has_many PitchDeckSection
- Constitution has_many Principle, has_many TraceabilityLink
- Strategic Constitution referenced_by Feature Constitution
- AnalysisReport contains ValidationError/Warning/Info
- Checklist validates Constitution, contains ChecklistItem

### Contracts

**Document**: [contracts/slash-commands.yaml](./contracts/slash-commands.yaml) - completed

**Command Interfaces**:

1. `/bp.clarify`:
   - Parameters: `--section` (optional), `--dry-run` (optional)
   - Output: Updated pitch deck, version bump, list of changes
   - Performance: <10 seconds

2. `/bp.analyze`:
   - Parameters: `--verbose` (optional), `--fix` (optional)
   - Output: Analysis report, error/warning/info counts, changelog entry
   - Performance: <2 seconds

3. `/bp.checklist`:
   - Parameters: `--report` (optional), `--force` (optional)
   - Output: Generated checklists or completion report
   - Performance: <5 seconds

**Error Handling**: Defined error types with HTTP equivalents (file_not_found=404, invalid_parameter=400, parse_error=422, version_error=409, user_abort=499).

**Workflow Integration**: Recommended sequence is clarify → decompose → analyze → checklist → implement.

### Quickstart

**Document**: [quickstart.md](./quickstart.md) - completed

**Scenarios Covered**:
1. Clarify vague pitch deck (5 minutes)
2. Validate constitutions after decomposition (3 minutes)
3. Generate quality checklists (2 minutes)
4. Focus clarification on specific section (2 minutes)
5. Dry run clarification (2 minutes)

**Complete Workflow Example**: 15-minute end-to-end walkthrough from pitch deck creation to implementation readiness.

**Common Issues & Solutions**: 6 troubleshooting scenarios with recovery steps.

### Agent Context Update

**Updated**: [CLAUDE.md](../../CLAUDE.md) - completed by script

**Added Technology**:
- Database: N/A (file-based markdown storage)
- Project type: Single Python CLI package

## Post-Design Constitution Re-Check

*Re-evaluating after Phase 1 design completion...*

### I. Speckit Architecture Clone ✅ PASS

**Design Validation**:
- Source structure mirrors BP-Kit Init: `src/bpkit_cli/commands/`, `src/bpkit_cli/models/`, `src/bpkit_cli/core/`
- Slash commands follow standard naming: `bp.*.md` in `.claude/commands/`
- No new CLI entry points - extends existing `bpkit` command
- Templates use Jinja2 (industry standard, no proprietary formats)

**Post-Design Status**: ✅ Architecture remains aligned with Speckit/BP-Kit patterns.

### II. Business-to-Code Bridge ✅ PASS

**Design Validation**:
- Data model includes PitchDeck + Constitution entities (bridges business → technical)
- TraceabilityLink enforces 2-level structure (pitch deck → strategic → feature)
- ClarificationQuestion fills gaps in pitch deck (input quality for decomposition)
- Checklist validates AI-executable criteria (completeness, testability, traceability)

**Post-Design Status**: ✅ Design strengthens business-to-code pipeline.

### III. Bidirectional Traceability ✅ PASS

**Design Validation**:
- TraceabilityLink model with source_file, source_line, target_file, target_section
- LinkValidator validates both file existence and section ID existence
- AnalysisReport tracks broken links with file path + line number
- VersionTracker detects mismatches between constitution and pitch deck versions
- Changelog integration (reports saved to `.specify/changelog/`)

**Post-Design Status**: ✅ Design enforces bidirectional traceability.

### IV. Speckit Compatibility ✅ PASS

**Design Validation**:
- Checklist items include "Ready for /speckit.plan" criterion
- No constitution format modifications (read-only analysis)
- Commands run BEFORE `/speckit.plan` (pre-flight checks)
- Quickstart integrates BP-Kit quality commands with Speckit workflow

**Post-Design Status**: ✅ Design maintains Speckit compatibility.

### V. AI-Executable Specifications ✅ PASS

**Design Validation**:
- AmbiguityDetector identifies [NEEDS CLARIFICATION] patterns
- ConflictDetector finds contradictory principles
- Checklist validates completeness (user stories, data models, success criteria all present)
- ClarificationQuestion resolves ambiguities that would block AI agents

**Post-Design Status**: ✅ Design improves AI specification quality.

**Overall Post-Design Check**: ✅ **PASSED** - All principles remain aligned after design phase.

## Implementation Notes

### Key Technical Decisions

**1. Why markdown-it-py over other parsers?**
- Already transitive dependency via Rich (no new dependency)
- CommonMark compliant (handles GFM extensions)
- Token-based parsing (efficient for large files)
- Active maintenance (last update < 6 months)

**2. Why lightweight pattern matching vs NLP?**
- Domain-specific (Sequoia template structure)
- Fast (<50ms per section)
- No external API dependencies
- No 50MB+ model downloads

**3. Why Jinja2 for checklists?**
- Industry standard template engine
- Separation of concerns (logic vs presentation)
- Extensible (users can customize templates)
- Minimal dependencies (pure Python)

**4. Why semantic versioning in YAML frontmatter?**
- Git-friendly (text-based)
- Automation-friendly (easy to parse)
- Speckit-compatible (same pattern)
- No database required

### Performance Optimizations

**1. Lazy Loading**:
- Parse constitutions only when needed (not all at once)
- Cache parsed documents during single command execution

**2. Parallel Validation**:
- Validate links in parallel using asyncio
- Target: 100+ links validated in <500ms

**3. Efficient Parsing**:
- Use markdown-it-py token stream (don't render HTML)
- Build section ID index once per file for O(1) lookup

**4. Early Exit**:
- `/bp.clarify` stops after 5 questions (don't process entire deck if already clear)
- `/bp.analyze` can skip verbose mode for faster results

### Edge Cases Handled

**1. Circular Dependencies**:
- Feature A depends on Feature B which depends on Feature A
- Detection: Track visited features during traversal, report WARNING if cycle detected

**2. Version Mismatches**:
- Constitution references pitch deck v1.0.0 but current is v2.0.0
- Detection: Parse versions, compare using semver rules, report WARNING with suggestion to run `/bp.sync`

**3. Missing Section IDs**:
- Link references `#principle-5` but file only has `#principle-1` through `#principle-4`
- Detection: Extract all heading IDs, validate against link targets, report ERROR with line number

**4. Empty Pitch Deck Sections**:
- Section exists but contains only placeholders ("[TBD]", "[X]", etc.)
- Detection: Pattern matching for vague indicators, prompt user for clarification

**5. Manual Edits After Decomposition**:
- User manually changes constitution after `/bp.decompose`
- Detection: `/bp.analyze` still validates links (doesn't assume auto-generated = correct)

### Testing Strategy

**Unit Tests** (8 files):
- `test_markdown_parser.py` - Token extraction, section ID parsing
- `test_link_validator.py` - File existence, section ID validation
- `test_ambiguity_detector.py` - Pattern matching for vague phrases
- `test_conflict_detector.py` - Contradiction detection logic
- `test_version_tracker.py` - Semver parsing and comparison
- `test_pitch_deck_model.py` - PitchDeck entity methods
- `test_constitution_model.py` - Constitution entity methods
- `test_checklist_model.py` - Checklist parsing and completion tracking

**Integration Tests** (3 files):
- `test_clarify_command.py` - End-to-end `/bp.clarify` workflow
- `test_analyze_command.py` - End-to-end `/bp.analyze` workflow with errors/warnings
- `test_checklist_command.py` - End-to-end `/bp.checklist` generation and reporting

**Test Fixtures**:
- `sample-pitch-deck.md` - Mock Sequoia template with some vague sections
- `sample-strategic-constitution.md` - Mock with valid and broken links
- `sample-feature-constitution.md` - Mock with principles and traceability links

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| markdown-it-py breaking changes | Low | Medium | Pin exact version, monitor releases |
| User confusion with interactive Q&A | Medium | Medium | Provide examples, dry-run mode |
| Performance degradation with large projects (50+ constitutions) | Low | Medium | Lazy loading, parallel validation, early benchmarking |
| Checklist items become stale | Medium | Low | Version checklist templates, document customization process |
| False positive ambiguity detection | Medium | Low | Tunable thresholds, dry-run mode for preview |

**Overall Risk Level**: LOW - All risks have mitigation strategies, no high-impact/high-likelihood combinations.

## Next Steps

**✅ Phase 0 (Research)**: COMPLETED - All technical unknowns resolved.

**✅ Phase 1 (Design)**: COMPLETED - Data model, contracts, quickstart all created.

**⏭️ Phase 2 (Tasks)**: NEXT - Run `/speckit.tasks` to generate actionable task list.

**Implementation Readiness**: ✅ **READY** - All design artifacts complete, no blockers identified.

---

**Generated**: 2025-10-10
**Status**: Planning Complete, Ready for `/speckit.tasks`
**Constitution Compliance**: ✅ PASSED (all 5 principles aligned)
**Estimated Implementation Time**: 12-16 hours (based on 3 commands × 4-5 hours each)
