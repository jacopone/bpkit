# Tasks: BP-Kit Quality Commands

**Input**: Design documents from `/specs/002-bp-kit-quality/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested in spec - test tasks excluded per template rules

**Organization**: Tasks grouped by user story (P1: clarify, P1: analyze, P2: checklist) to enable independent implementation

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1=/bp.clarify, US2=/bp.analyze, US3=/bp.checklist)
- Paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency setup

- [X] T001 Add dependencies to `pyproject.toml`: markdown-it-py, jinja2, pyyaml (if not present)
- [X] T002 [P] Create `src/bpkit_cli/models/__init__.py` and export placeholders for new models
- [X] T003 [P] Create `src/bpkit_cli/core/__init__.py` and export placeholders for new core modules
- [X] T004 [P] Create directory `src/bpkit_cli/templates/` for Jinja2 templates
- [X] T005 [P] Create directory `.claude/commands/` (if not exists) for slash commands

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core parsing, models, and utilities needed by ALL user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Parsing Infrastructure

- [X] T006 Implement `src/bpkit_cli/core/markdown_parser.py` with MarkdownParser class
  - Methods: `parse_file()`, `extract_sections()`, `extract_heading_ids()`, `extract_links()`
  - Use markdown-it-py for CommonMark parsing with token stream
  - Return section metadata (id, title, content, line_start, line_end)

- [X] T007 Implement `src/bpkit_cli/core/version_tracker.py` with VersionTracker class
  - Methods: `parse_version()`, `compare_versions()`, `bump_version(bump_type)`
  - Support semantic versioning (MAJOR.MINOR.PATCH)
  - Parse YAML frontmatter for version extraction

### Core Data Models (Shared by All Stories)

- [X] T008 [P] Implement `src/bpkit_cli/models/pitch_deck.py`
  - Classes: `PitchDeck`, `PitchDeckSection`
  - Methods: `parse()`, `get_section()`, `update_section()`, `bump_version()`
  - Integration with MarkdownParser for section extraction

- [X] T009 [P] Implement `src/bpkit_cli/models/constitution.py`
  - Classes: `Constitution`, `Principle`, `ConstitutionType` enum
  - Methods: `parse()`, `get_principle()`, `validate_links()`
  - Track upstream/downstream links

- [X] T010 [P] Implement `src/bpkit_cli/models/traceability.py`
  - Classes: `TraceabilityLink`, `LinkType` enum, `LinkValidationResult`
  - State machine: CREATED → VALID/BROKEN_FILE/BROKEN_SECTION/MISSING_SOURCE
  - Methods: `validate()`, `get_target()`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Clarify Ambiguous Pitch Deck (Priority: P1) 🎯 MVP

**Goal**: Implement `/bp.clarify` command to identify and resolve pitch deck ambiguities

**Independent Test**: Run `/bp.clarify` on pitch deck with vague sections, system asks 3-5 questions, user answers, deck updated with version bump

### US1 Models & Core Logic

- [X] T011 [P] [US1] Implement `src/bpkit_cli/models/clarification.py`
  - Classes: `ClarificationQuestion`, `Priority` enum (HIGH/MEDIUM/LOW)
  - State machine: CREATED → ANSWERED → APPLIED
  - Methods: `ask_interactively()`, `update_pitch_deck()`

- [X] T012 [P] [US1] Implement `src/bpkit_cli/core/ambiguity_detector.py`
  - Class: `AmbiguityDetector`
  - Methods: `detect_vague_sections()`, `prioritize_questions()`, `generate_question()`
  - Pattern matching for: [TBD], [X], vague phrases, missing required content
  - Domain-specific heuristics for Sequoia template sections

### US1 Command Implementation

- [X] T013 [US1] Implement `src/bpkit_cli/commands/clarify.py`
  - Function: `clarify(section: Optional[str], dry_run: bool)`
  - Steps: Parse deck → Detect ambiguities → Generate questions (max 5, prioritized) → Present to user → Update deck → Bump version
  - Support `--section` flag for targeted clarification
  - Support `--dry-run` flag for preview mode

- [X] T014 [US1] Create slash command `.claude/commands/bp.clarify.md`
  - Description: Analyze pitch deck for ambiguities and prompt for clarifications
  - Parameters: --section (optional), --dry-run (optional)
  - Example usage from quickstart.md scenarios
  - Links to contracts/slash-commands.yaml specification

- [X] T015 [US1] Update `src/bpkit_cli/commands/__init__.py` to register `clarify` command
  - Add Typer command with proper help text
  - Ensure command is accessible via `bpkit clarify`

### US1 Integration & Polish

- [X] T016 [US1] Add logging to `.specify/changelog/` for clarify operations
  - Log format: timestamp, questions asked, answers provided, sections updated, version change
  - Filename: `YYYY-MM-DD-clarify-<section>.md` or `YYYY-MM-DD-clarify-full.md`

- [X] T017 [US1] Handle edge case: clarify after decomposition (warn user about regeneration)
  - Check if `.specify/memory/` or `.specify/features/` exist
  - Display warning: "Pitch deck already decomposed. Re-run /bp.decompose after clarification."

**Checkpoint**: User Story 1 complete - `/bp.clarify` functional and independently testable

---

## Phase 4: User Story 2 - Validate Constitution Consistency (Priority: P1)

**Goal**: Implement `/bp.analyze` command to validate constitutional traceability and consistency

**Independent Test**: Run `/bp.analyze` after decomposition, system validates all links, detects conflicts, reports coverage gaps

### US2 Models & Core Logic

- [X] T018 [P] [US2] Implement `src/bpkit_cli/models/analysis.py`
  - Classes: `AnalysisReport`, `ValidationError`, `ValidationWarning`, `ValidationInfo`, `Severity` enum
  - Methods: `has_errors()`, `has_warnings()`, `is_passing()`, `format_summary()`, `save_to_changelog()`
  - Organize issues by severity and file path

- [X] T019 [P] [US2] Implement `src/bpkit_cli/core/link_validator.py`
  - Class: `LinkValidator`
  - Methods: `extract_links()`, `validate_link()`, `validate_all_links()` (parallel with asyncio)
  - Check file existence and section ID existence
  - Return detailed error messages with line numbers

- [X] T020 [P] [US2] Implement `src/bpkit_cli/core/conflict_detector.py`
  - Class: `ConflictDetector`
  - Methods: `detect_conflicts()`, `check_coverage()`, `validate_version_consistency()`
  - Detect contradictory principles across strategic constitutions
  - Identify pitch deck sections not referenced by any constitution

### US2 Command Implementation

- [X] T021 [US2] Implement `src/bpkit_cli/commands/analyze.py`
  - Function: `analyze(verbose: bool, fix: bool)`
  - Steps: Scan constitutions → Validate links → Detect conflicts → Check coverage → Check versions → Generate report → Save to changelog → Display summary
  - Support `--verbose` flag for detailed output
  - Support `--fix` flag for auto-fixing simple issues (future: version mismatches only)

- [X] T022 [US2] Create slash command `.claude/commands/bp.analyze.md`
  - Description: Validate constitutional consistency and traceability
  - Parameters: --verbose (optional), --fix (optional)
  - Example usage from quickstart.md scenarios
  - Links to contracts/slash-commands.yaml specification

- [X] T023 [US2] Update `src/bpkit_cli/commands/__init__.py` to register `analyze` command
  - Add Typer command with proper help text
  - Ensure command is accessible via `bpkit analyze`

### US2 Integration & Polish

- [X] T024 [US2] Save analysis reports to `.specify/changelog/YYYY-MM-DD-analyze-report.md`
  - Include: timestamp, pitch deck version, constitutions analyzed, errors, warnings, info
  - Format report with markdown tables for readability

- [X] T025 [US2] Handle edge case: circular dependencies between features
  - Track visited features during traversal
  - Report WARNING with cycle path (Feature A → Feature B → Feature A)

- [X] T026 [US2] Handle edge case: missing section IDs in target files
  - Extract all heading IDs from target markdown
  - Report ERROR with actual available section IDs for user reference

**Checkpoint**: User Story 2 complete - `/bp.analyze` functional and independently testable

---

## Phase 5: User Story 3 - Generate Quality Checklists (Priority: P2)

**Goal**: Implement `/bp.checklist` command to generate structured validation checklists

**Independent Test**: Run `/bp.checklist` after decomposition, generates checklists in `.specify/checklists/`, run `--report` to show completion status

### US3 Models & Templates

- [X] T027 [P] [US3] Implement `src/bpkit_cli/models/checklist.py`
  - Classes: `Checklist`, `ChecklistItem`
  - Methods: `calculate_completion()`, `add_item()`, `parse_from_file()`, `save_to_file()`
  - Parse markdown checkboxes ([ ] vs [x])
  - Track completion percentage

- [X] T028 [P] [US3] Create Jinja2 template `src/bpkit_cli/templates/strategic-checklist.j2`
  - 10 items per contracts/slash-commands.yaml specification
  - Categories: Traceability (4), Quality (3), Completeness (3)
  - Items: measurable outcomes, pitch deck links, no implementation details, version tracking, testable principles, downstream references, rationale, examples, amendment process, review cycle

- [X] T029 [P] [US3] Create Jinja2 template `src/bpkit_cli/templates/feature-checklist.j2`
  - 15 items per contracts/slash-commands.yaml specification
  - Categories: Traceability, Quality, Completeness
  - Items: user stories with acceptance criteria, measurable success, strategic links, data model entities, relationships, no [NEEDS CLARIFICATION], MVP boundaries, dependencies, edge cases, non-functional reqs, principles with sources, API contracts, state transitions, security, ready for /speckit.plan

### US3 Command Implementation

- [X] T030 [US3] Implement `src/bpkit_cli/commands/checklist.py`
  - Function: `checklist(report: bool, force: bool)`
  - Generate mode: Scan constitutions → Determine type (strategic vs feature) → Load template → Render → Save to .specify/checklists/
  - Report mode: Parse checklists → Calculate completion → Display table
  - Support `--report` flag for completion status
  - Support `--force` flag to overwrite existing checklists

- [X] T031 [US3] Create slash command `.claude/commands/bp.checklist.md`
  - Description: Generate quality validation checklists for all constitutions
  - Parameters: --report (optional), --force (optional)
  - Example usage from quickstart.md scenarios
  - Links to contracts/slash-commands.yaml specification

- [X] T032 [US3] Update `src/bpkit_cli/commands/__init__.py` to register `checklist` command
  - Add Typer command with proper help text
  - Ensure command is accessible via `bpkit checklist`

### US3 Integration & Polish

- [X] T033 [US3] Create `.specify/checklists/` directory during checklist generation (if not exists)
  - Ensure directory is .gitignore-friendly (checklists are user-editable)

- [X] T034 [US3] Format `--report` output as markdown table
  - Columns: Constitution | Completion | Remaining
  - Include overall status line: "XX% complete (N items remaining)"
  - Color-code completion (✅ for 100%, percentages for incomplete)

- [X] T035 [US3] Handle edge case: checklist run before decomposition
  - Check if `.specify/memory/` and `.specify/features/` exist
  - Display error: "No constitutions found. Run /bp.decompose first."

**Checkpoint**: User Story 3 complete - `/bp.checklist` functional and independently testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories

- [x] T036 [P] Add Rich console formatting to all command outputs
  - Use Rich tables for reports, progress bars for long operations, color-coded severity

- [x] T037 [P] Add comprehensive docstrings to all public classes and methods
  - Follow Google docstring format, include examples

- [x] T038 Update main `README.md` with BP-Kit Quality Commands section
  - Brief description of 3 commands
  - Link to quickstart.md for detailed usage
  - Workflow integration diagram

- [x] T039 Validate implementation against quickstart.md scenarios
  - Test all 5 scenarios from quickstart.md
  - Verify common issues & solutions section accuracy

- [x] T040 Run full quality workflow on real pitch deck
  - Use AirBnB example or create test pitch deck
  - Verify: clarify → decompose → analyze → checklist → report
  - Document any discrepancies or edge cases

- [x] T041 [P] Performance benchmarking
  - `/bp.clarify` on typical pitch deck (target: <10s)
  - `/bp.analyze` on 10 constitutions (target: <2s)
  - `/bp.checklist` generation (target: <5s)
  - Document actual performance vs targets

- [x] T042 Update `.specify/changelog/` with feature summary
  - Document: feature added, commands available, integration points with existing workflow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - No dependencies on other stories
- **User Story 2 (Phase 4)**: Depends on Foundational completion - No dependencies on other stories
- **User Story 3 (Phase 5)**: Depends on Foundational completion - No dependencies on other stories
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Independence

- **US1 (/bp.clarify)**: Fully independent - works on pitch deck before decomposition
- **US2 (/bp.analyze)**: Fully independent - works on constitutions after decomposition
- **US3 (/bp.checklist)**: Fully independent - generates checklists from constitutions

All three user stories can be implemented in parallel after Foundational phase completes (if team capacity allows).

### Within Each User Story

- Models/Core logic before command implementation
- Command implementation before slash command file
- Slash command before registration in `__init__.py`
- Core functionality before edge case handling

### Parallel Opportunities

**Setup Phase**:
- T002, T003, T004, T005 can all run in parallel (different directories)

**Foundational Phase**:
- T008, T009, T010 can run in parallel (different model files)

**User Story 1**:
- T011, T012 can run in parallel (different files)

**User Story 2**:
- T018, T019, T020 can run in parallel (different files)

**User Story 3**:
- T027, T028, T029 can run in parallel (model + 2 templates)

**Polish Phase**:
- T036, T037, T041 can run in parallel (independent improvements)

---

## Parallel Example: Foundational Phase

```bash
# Launch all core models in parallel:
Task T008: "Implement src/bpkit_cli/models/pitch_deck.py"
Task T009: "Implement src/bpkit_cli/models/constitution.py"
Task T010: "Implement src/bpkit_cli/models/traceability.py"
```

## Parallel Example: User Story 1 Models

```bash
# Launch clarify-specific models in parallel:
Task T011: "Implement src/bpkit_cli/models/clarification.py"
Task T012: "Implement src/bpkit_cli/core/ambiguity_detector.py"
```

## Parallel Example: User Story 3 Templates

```bash
# Launch all checklist components in parallel:
Task T027: "Implement src/bpkit_cli/models/checklist.py"
Task T028: "Create src/bpkit_cli/templates/strategic-checklist.j2"
Task T029: "Create src/bpkit_cli/templates/feature-checklist.j2"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only - Both P1)

**Rationale**: P1 stories provide core value - clarify before decomposition, analyze after decomposition

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (/bp.clarify)
4. Complete Phase 4: User Story 2 (/bp.analyze)
5. **STOP and VALIDATE**: Test both commands with real pitch deck
6. Deploy/demo if ready

**MVP Scope**: 42 tasks (T001-T026 + Phase 6 essentials)
**Estimated Time**: 8-10 hours

### Incremental Delivery

1. **Foundation** (T001-T010): Core parsing + models → 3-4 hours
2. **MVP** (T011-T026): Clarify + Analyze commands → 5-6 hours
3. **Full Feature** (T027-T035): Checklist command → 3-4 hours
4. **Polish** (T036-T042): Documentation, performance, validation → 2-3 hours

**Total Estimated Time**: 13-17 hours (aligns with plan.md estimate of 12-16 hours)

### Parallel Team Strategy

With 2 developers after Foundational phase completes:

- **Developer A**: User Story 1 (/bp.clarify) → T011-T017
- **Developer B**: User Story 2 (/bp.analyze) → T018-T026

Then combine for User Story 3 or have Developer A handle it solo (smaller scope).

---

## Task Summary

**Total Tasks**: 42
- Setup: 5 tasks
- Foundational: 5 tasks (BLOCKING)
- User Story 1 (/bp.clarify): 7 tasks
- User Story 2 (/bp.analyze): 9 tasks
- User Story 3 (/bp.checklist): 9 tasks
- Polish: 7 tasks

**Parallel Opportunities**: 15 tasks marked [P] (35% can run concurrently)

**Independent Test Criteria**:
- US1: Run clarify on vague pitch deck, answer questions, verify updates
- US2: Run analyze on constitutions with intentional errors, verify detection
- US3: Run checklist generation, verify template rendering, test --report mode

**Suggested MVP Scope**: Setup + Foundational + US1 + US2 (26 core tasks) = 8-10 hours

---

## Notes

- All paths relative to repository root
- [P] = Different files, no dependencies
- [Story] = Maps to user story for traceability (US1, US2, US3)
- Each user story is independently testable after completion
- Commit after each task or logical group (e.g., all models in a story)
- Stop at checkpoints to validate story independence
- User Story 3 (checklist) is P2, can be deferred if needed for faster MVP

**Next Step**: Run `/speckit.implement` to begin implementation with task tracking
