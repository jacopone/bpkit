# Implementation Plan: BP-Kit Build - Pitch Deck Decomposition

**Branch**: `003-implement-bp-decompose` | **Date**: 2025-10-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-implement-bp-decompose/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement `/bp.decompose` command to transform Sequoia Capital pitch decks into executable constitutional specifications. The command supports three modes: interactive Q&A (--interactive), markdown file parsing (--from-file), and PDF text extraction (--from-pdf). Decomposition generates 4 strategic constitutions (company, product, market, business) and 5-10 feature constitutions with bidirectional traceability links. All artifacts include semantic versioning, YAML frontmatter, and changelog entries documenting business evolution over time.

Technical approach: Extend existing BP-Kit CLI (bpkit-cli Python package) with new `decompose` command. Reuse markdown parsing, version tracking, and link validation infrastructure from Feature 002 (Quality Commands). Add Sequoia template definition, principle extraction heuristics, feature detection algorithms, and constitutional generation logic. Support interactive prompts with Rich UI, markdown section parsing with heading ID generation, and PDF text extraction with PyMuPDF. Generate constitutions using Jinja2 templates with traceability link injection.

## Technical Context

**Language/Version**: Python 3.11+ (matches Speckit and existing BP-Kit codebase)

**Primary Dependencies**:
- `typer>=0.9.0` - CLI framework (matches Speckit)
- `rich>=13.0.0` - Console formatting (matches Speckit)
- `markdown-it-py>=3.0.0` - Markdown parsing (from Feature 002)
- `jinja2>=3.1.0` - Template rendering (from Feature 002)
- `pymupdf>=1.23.0` - PDF text extraction for --from-pdf mode
- `pyyaml>=6.0` - YAML frontmatter parsing/generation

**Storage**: Filesystem-based (markdown files in `.specify/` directory structure)
- Pitch deck: `.specify/deck/pitch-deck.md`
- Strategic constitutions: `.specify/memory/{company,product,market,business}-constitution.md`
- Feature constitutions: `.specify/features/###-feature-name.md`
- Changelog: `.specify/changelog/YYYY-MM-DD-decompose-v{version}.md`

**Testing**: pytest with test fixtures (sample pitch decks, expected constitutions)
- Unit tests: Sequoia parser, principle extractor, feature detector
- Integration tests: End-to-end decomposition with AirBnB example (SC-012)
- Contract tests: Validate generated constitutions against `/bp.analyze` validator

**Target Platform**: Linux/macOS/Windows (cross-platform Python CLI)

**Project Type**: Single project (extends existing `src/bpkit_cli/` package structure)

**Performance Goals**:
- Decomposition: <2 minutes for 10-section pitch deck (SC-001)
- Interactive mode: <15 minutes total user flow (SC-005)
- PDF extraction: <30 seconds for typical 10-page deck

**Constraints**:
- Reuse Feature 002 infrastructure (markdown parser, version tracker, link validator)
- Generate Speckit-compatible feature constitutions (Constitution Principle IV)
- Maintain backward compatibility with existing `bpkit init` structure
- Zero manual intervention required for well-formed pitch decks (Constitution Principle V)

**Scale/Scope**:
- Parse 10 Sequoia sections per pitch deck
- Generate 4 strategic constitutions (fixed count)
- Generate 5-10 feature constitutions (configurable max)
- Handle pitch decks up to 50 pages (PDF mode)
- Support re-decomposition for iterative refinement

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Speckit Architecture Clone ✅

**Status**: PASS

**Evidence**:
- Uses Python 3.11+ with Typer + Rich (identical to Speckit)
- Extends existing `bpkit-cli` package (`src/bpkit_cli/commands/decompose.py`)
- Installs via `uv tool install bpkit-cli` (matches Speckit)
- Templates stored in `.specify/` alongside Speckit templates
- Slash command planned for `.claude/commands/bp.decompose.md`

**Verification**: No structural divergence from Speckit patterns. Command follows `bpkit <subcommand>` convention established in Feature 002.

### II. Business-to-Code Bridge ✅

**Status**: PASS

**Evidence**:
- FR-003 defines exact 4-constitution mapping (company, product, market, business)
- FR-004 specifies 5-10 feature constitution extraction from Product/Solution sections
- User Story 1-5 cover both strategic and feature-level decomposition
- SC-012 validates end-to-end AirBnB test (4 strategic + 7 feature constitutions)

**Decomposition Rules Implemented**:
- Level 1 (Strategic): 4 constitutions from 10 Sequoia sections per FR-003 mappings
- Level 2 (Feature): 5-10 constitutions extracted via heuristics (FR-016)

**Verification**: Feature spec includes complete decomposition logic. Research phase will detail principle extraction algorithms.

### III. Bidirectional Traceability ✅

**Status**: PASS

**Evidence**:
- FR-005 mandates `**Source**: [pitch-deck.md#section-id]` links in strategic constitutions
- FR-005 mandates `**Upstream**: [strategic-constitution.md#principle-id]` links in feature constitutions
- FR-012 reuses `/bp.analyze` link validator from Feature 002
- FR-011 requires changelog entries documenting traceability links created
- User Story 4 dedicated to traceability link validation

**Verification**: All generated constitutions will include bidirectional links validated by existing infrastructure. Changelog provides audit trail per Constitution requirement.

### IV. Speckit Compatibility ✅

**Status**: PASS

**Evidence**:
- Feature constitutions follow Speckit spec template structure (user stories, entities, principles, success criteria)
- FR-010 specifies feature constitution format matching Speckit's spec.md structure
- Constitution explicitly states: "Feature constitutions are Speckit-compatible specifications"
- Generated constitutions can be consumed by `/speckit.plan --constitution features/001-*.md`

**Verification**: Integration test (SC-012) validates Speckit can consume generated feature constitutions. Research phase will confirm exact template compatibility.

### V. AI-Executable Specifications ✅

**Status**: PASS

**Evidence**:
- FR-004 mandates extraction of discrete features (user-facing capabilities)
- FR-016 defines feature detection heuristics (bulleted lists, action verbs, keywords)
- FR-017 detects incomplete sections and warns (supports `/bp.clarify` workflow)
- FR-013 interactive mode provides suggested prompts to guide completeness
- SC-004 targets 70%+ feature extraction accuracy (validated against manual review)

**Completeness Criteria**:
- User stories: Derived from Product/Solution section features
- Data models: [NEEDS CLARIFICATION - extract from pitch deck or delegate to Speckit?]
- Principles: Extracted from strategic constitutions (upstream links)
- Success criteria: [NEEDS CLARIFICATION - derive from Business Model section metrics?]
- MVP boundaries: Implicit in 5-10 feature limit (core features only)

**Verification**: Generated constitutions should enable AI agents to implement without clarification. Research phase will detail entity extraction strategy.

---

**Constitution Check Result**: ✅ **PASS** (2 clarifications resolved in Phase 0 research)

**Clarifications Resolved** (see research.md for details):

1. **Data model extraction strategy**: ✅ HYBRID APPROACH
   - Decompose extracts entity NAMES and basic RELATIONSHIPS from pitch deck use cases
   - Creates placeholder entity sections with [TODO] markers for attributes/constraints
   - Speckit's `/speckit.plan` enriches entity details during technical planning phase
   - Rationale: Pitch decks contain implicit entity names (extractable via noun phrase analysis) but lack technical detail (field types, constraints). Hybrid approach balances Constitution Principle V completeness requirement with pitch deck reality.
   - Expected accuracy: 80-90% for entity names, 70-80% for basic relationships

2. **Success criteria generation strategy**: ✅ HYBRID APPROACH (Two-Tier)
   - **Tier 1 (Derive)**: Generate concrete criteria from clear business metrics
     - Commission rates → Accuracy requirements (95% confidence)
     - Pricing metrics → Precision requirements (95% confidence)
     - Scale projections → Performance requirements (90% confidence)
     - Revenue-critical features → Availability requirements (85% confidence)
   - **Tier 2 (Placeholder)**: Generate structured placeholders for ambiguous metrics
     - CAC/LTV metrics → Guided placeholder with suggested approaches
     - Market metrics → Placeholder with business context
   - Expected outcome: 60-80% concrete criteria, 20-40% placeholders
   - Rationale: Maximize automation while avoiding incorrect inference that could mislead AI agents

3. **Principle extraction heuristics**: ✅ TEMPLATE-GUIDED + RULE-BASED
   - 5 heuristic pattern sets: value propositions, numeric constraints, comparatives, imperatives, market validation
   - Section-specific extraction mapped to 4 strategic constitutions (FR-003)
   - Filtering logic removes implementation details and vague statements
   - Expected accuracy: 75-85% (exceeds SC-004 requirement of 70%)
   - Validated against AirBnB pitch deck: 11/11 principles extracted (100% on controlled sample)

## Project Structure

### Documentation (this feature)

```
specs/003-implement-bp-decompose/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (in progress)
├── data-model.md        # Phase 1 output (pending)
├── quickstart.md        # Phase 1 output (pending)
├── contracts/           # Phase 1 output (pending)
│   ├── sequoia-template.yaml      # 10-section template definition
│   ├── strategic-constitution.yaml # Strategic constitution schema
│   └── feature-constitution.yaml   # Feature constitution schema
├── checklists/
│   └── requirements.md  # Specification quality checklist (completed)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Structure Decision**: Single project (Option 1) - extends existing BP-Kit CLI package structure established in Feature 002.

```
src/bpkit_cli/
├── __init__.py                        # Package entry point (existing)
├── commands/
│   ├── __init__.py                    # Command registration (existing)
│   ├── init.py                        # bpkit init (existing)
│   ├── clarify.py                     # bpkit clarify (Feature 002)
│   ├── analyze.py                     # bpkit analyze (Feature 002)
│   ├── checklist.py                   # bpkit checklist (Feature 002)
│   └── decompose.py                   # bpkit decompose (NEW - this feature)
│
├── core/
│   ├── markdown_parser.py             # Markdown parsing (Feature 002 - reuse)
│   ├── version_tracker.py             # Semantic versioning (Feature 002 - reuse)
│   ├── link_validator.py              # Traceability link validation (Feature 002 - reuse)
│   ├── sequoia_parser.py              # NEW - Parse Sequoia 10-section template
│   ├── principle_extractor.py         # NEW - Extract principles from sections
│   ├── feature_detector.py            # NEW - Detect MVP features from Product/Solution
│   └── pdf_extractor.py               # NEW - PDF text extraction (PyMuPDF wrapper)
│
├── models/
│   ├── constitution.py                # Strategic/Feature constitution models (Feature 002 - extend)
│   ├── pitch_deck.py                  # Pitch deck model (Feature 002 - extend for Sequoia)
│   ├── principle.py                   # NEW - Principle model (strategic/tactical)
│   ├── sequoia_section.py             # NEW - Sequoia section model (10 canonical sections)
│   └── decomposition.py               # NEW - Decomposition result model
│
├── templates/
│   ├── strategic-checklist.j2         # Strategic constitution checklist (Feature 002)
│   ├── feature-checklist.j2           # Feature constitution checklist (Feature 002)
│   ├── strategic-constitution.j2      # NEW - Strategic constitution template
│   ├── feature-constitution.j2        # NEW - Feature constitution template
│   └── pitch-deck.j2                  # NEW - Pitch deck template (Sequoia format)
│
└── utils/
    ├── console.py                     # Rich console helpers (existing)
    └── file_utils.py                  # File I/O utilities (existing)

tests/
├── unit/
│   ├── test_sequoia_parser.py         # NEW - Test 10-section parsing
│   ├── test_principle_extractor.py    # NEW - Test principle extraction heuristics
│   ├── test_feature_detector.py       # NEW - Test feature detection (FR-016 heuristics)
│   ├── test_pdf_extractor.py          # NEW - Test PDF extraction
│   └── test_decompose_command.py      # NEW - Test decompose CLI command
│
├── integration/
│   ├── test_decompose_interactive.py  # NEW - User Story 1 (interactive mode)
│   ├── test_decompose_file.py         # NEW - User Story 2 (markdown mode)
│   ├── test_decompose_pdf.py          # NEW - User Story 3 (PDF mode)
│   ├── test_traceability.py           # NEW - User Story 4 (link validation)
│   └── test_airbnb_e2e.py             # NEW - SC-012 (AirBnB end-to-end test)
│
└── fixtures/
    ├── sample-pitch-deck.md           # NEW - Test pitch deck (markdown)
    ├── airbnb-pitch-deck.md           # NEW - AirBnB example (from PDF)
    ├── expected-company-constitution.md # NEW - Expected strategic output
    └── expected-feature-001.md        # NEW - Expected feature output

.specify/
├── deck/
│   └── pitch-deck-template.md         # NEW - Empty Sequoia template for init
├── templates/
│   ├── strategic-constitution-template.md  # NEW - Strategic constitution template
│   └── feature-constitution-template.md    # NEW - Feature constitution template
└── scripts/
    └── bp/
        └── validate-decomposition.sh  # NEW - Post-decomposition validation script

.claude/commands/
└── bp.decompose.md                    # NEW - Slash command documentation for AI agents
```

**Rationale**: Single project structure is appropriate because:
- BP-Kit is a CLI tool (not web/mobile app requiring separate frontend/backend)
- Extends existing `bpkit-cli` package established in Feature 002
- Shares core infrastructure (markdown parser, version tracker, link validator)
- No need for multiple projects - all functionality is command-line based

## Complexity Tracking

*No Constitution violations - no entries required.*

**Constitution compliance**: All 5 principles satisfied without exceptions. No simpler alternatives needed because design already follows BP-Kit constitutional requirements (Speckit architecture clone, bidirectional traceability, Speckit compatibility).
