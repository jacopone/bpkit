# Implementation Tasks: BP-Kit Build - Pitch Deck Decomposition

**Feature**: 003-implement-bp-decompose
**Branch**: `003-implement-bp-decompose`
**Total Tasks**: 45
**Estimated Time**: 18-22 hours

---

## Task Organization Strategy

Tasks are organized by **user story** to enable independent implementation and testing. Each story phase is a complete, independently testable increment.

**Phase Structure**:
1. **Setup** (T001-T006): Project initialization, shared infrastructure
2. **Foundational** (T007-T013): Blocking prerequisites for all user stories
3. **User Story 1 - Interactive Mode (P1)** (T014-T019): Interactive pitch deck creation
4. **User Story 2 - Markdown Mode (P1)** (T020-T023): Markdown file decomposition
5. **User Story 3 - PDF Mode (P2)** (T024-T027): PDF extraction and decomposition
6. **User Story 4 - Traceability (P1)** (T028-T032): Link validation integration
7. **User Story 5 - Versioning (P2)** (T033-T037): Version tracking and changelog
8. **Polish & Integration** (T038-T045): Cross-cutting concerns, documentation

---

## Phase 1: Setup (Shared Infrastructure)

### T001: Create decompose command entry point [P]
- **File**: `src/bpkit_cli/commands/decompose.py`
- **Story**: Setup
- **Action**: Create decompose.py with Typer command registration, three mode flags (--interactive, --from-file, --from-pdf), --dry-run flag
- **Dependencies**: None
- **Estimate**: 30 min

### T002: Define Sequoia section enum [P]
- **File**: `src/bpkit_cli/models/sequoia_section.py`
- **Story**: Setup
- **Action**: Create SequoiaSectionType enum with 10 canonical sections (COMPANY_PURPOSE through FINANCIALS), section-to-constitution mapping dict (FR-003)
- **Dependencies**: None
- **Estimate**: 20 min

### T003: Create Principle model [P]
- **File**: `src/bpkit_cli/models/principle.py`
- **Story**: Setup
- **Action**: Define Principle dataclass with id, text, type (STRATEGIC/TACTICAL), source_section_id, confidence, extraction_method attributes
- **Dependencies**: T002
- **Estimate**: 20 min

### T004: Create DecompositionResult model [P]
- **File**: `src/bpkit_cli/models/decomposition.py`
- **Story**: Setup
- **Action**: Define DecompositionResult dataclass with mode, pitch_deck_version, strategic/feature counts, links count, warnings, errors lists
- **Dependencies**: None
- **Estimate**: 20 min

### T005: Create Jinja2 templates for constitutions [P]
- **Files**: `src/bpkit_cli/templates/strategic-constitution.j2`, `feature-constitution.j2`, `pitch-deck.j2`
- **Story**: Setup
- **Action**: Create 3 Jinja2 templates with YAML frontmatter, traceability link placeholders, principle sections, entity stubs (feature template)
- **Dependencies**: None
- **Estimate**: 45 min

### T006: Extend PitchDeck model for Sequoia structure [P]
- **File**: `src/bpkit_cli/models/pitch_deck.py`
- **Story**: Setup
- **Action**: Add sections list (10 PitchDeckSection instances), source_mode (DecompositionMode enum), Sequoia template validation
- **Dependencies**: T002
- **Estimate**: 30 min

**Checkpoint**: Setup complete. Models, templates, and command entry point ready.

---

## Phase 2: Foundational (Blocking Prerequisites)

### T007: Implement Sequoia parser core
- **File**: `src/bpkit_cli/core/sequoia_parser.py`
- **Story**: Foundational
- **Action**: Create SequoiaParser class with parse_pitch_deck() method, detect 10 sections from markdown h2 headings, generate GitHub-style heading IDs (FR-014)
- **Dependencies**: T002, T006
- **Estimate**: 1 hour

### T008: Implement principle extraction heuristics
- **File**: `src/bpkit_cli/core/principle_extractor.py`
- **Story**: Foundational
- **Action**: Implement 5 heuristic pattern sets (VALUE_PROP, NUMERIC_CONSTRAINT, COMPARATIVE, IMPERATIVE, MARKET_NUMBER patterns), filtering logic (is_valid_principle), section-specific extraction
- **Dependencies**: T003, T007
- **Estimate**: 2 hours

### T009: Implement feature detection heuristics
- **File**: `src/bpkit_cli/core/feature_detector.py`
- **Story**: Foundational
- **Action**: Create FeatureDetector class, extract 5-10 features from Product/Solution sections using bulleted lists, action verbs, feature keywords (FR-016), priority assignment (P1/P2/P3)
- **Dependencies**: T007
- **Estimate**: 1.5 hours

### T010: Implement entity extraction (hybrid approach)
- **File**: `src/bpkit_cli/core/entity_extractor.py`
- **Story**: Foundational
- **Action**: Extract entity names (noun phrases), infer basic relationships (has_many/belongs_to from use case sentences), generate entity stubs with [TODO] placeholders for attributes/constraints
- **Dependencies**: T007
- **Estimate**: 1.5 hours

### T011: Implement success criteria generator (two-tier)
- **File**: `src/bpkit_cli/core/success_criteria_generator.py`
- **Story**: Foundational
- **Action**: Implement Tier 1 derivation rules (commission→accuracy, pricing→precision, scale→performance, criticality→availability), Tier 2 placeholder generation with guidance
- **Dependencies**: T007
- **Estimate**: 2 hours

### T012: Implement PDF extractor
- **File**: `src/bpkit_cli/core/pdf_extractor.py`
- **Story**: Foundational
- **Action**: Create PDFExtractor class using PyMuPDF, extract text with font size/style detection for section boundaries, handle multi-column layouts, report extraction confidence (FR-015)
- **Dependencies**: None
- **Estimate**: 2 hours

### T013: Implement constitutional generator core
- **File**: `src/bpkit_cli/core/constitution_generator.py`
- **Story**: Foundational
- **Action**: Create ConstitutionGenerator class, generate 4 strategic constitutions from principles (FR-003 mappings), generate 5-10 feature constitutions with entity stubs and success criteria, inject traceability links (FR-005)
- **Dependencies**: T003, T005, T008, T010, T011
- **Estimate**: 2.5 hours

**Checkpoint**: Foundational infrastructure complete. All extraction/generation logic implemented.

---

## Phase 3: User Story 1 - Interactive Pitch Deck Creation (P1)

**Goal**: Founder creates pitch deck from scratch via Q&A, generates constitutions.

**Independent Test**: Run `bpkit decompose --interactive`, answer 10 Sequoia questions, verify 4 strategic + N feature constitutions generated with valid traceability.

### T014: Implement interactive prompt system [US1]
- **File**: `src/bpkit_cli/commands/decompose.py` (interactive mode)
- **Story**: US1
- **Action**: Use Rich Prompt.ask() for multi-line input, display Sequoia section name + description + suggested prompts (FR-013), collect 10 section responses sequentially, allow skip (marks [TODO])
- **Dependencies**: T002, T006, T007
- **Estimate**: 1.5 hours

### T015: Build pitch deck from interactive input [US1]
- **File**: `src/bpkit_cli/commands/decompose.py` (interactive mode)
- **Story**: US1
- **Action**: Construct PitchDeck model from user responses, generate markdown with h2 headings + GitHub-style IDs, save to `.specify/deck/pitch-deck.md` (FR-008), set version 1.0.0
- **Dependencies**: T014
- **Estimate**: 1 hour

### T016: Decompose interactive pitch deck [US1]
- **File**: `src/bpkit_cli/commands/decompose.py` (interactive mode)
- **Story**: US1
- **Action**: Pass pitch deck to SequoiaParser → PrincipleExtractor → FeatureDetector → ConstitutionGenerator, generate 4 strategic + N feature constitutions, save to `.specify/memory/` and `.specify/features/`
- **Dependencies**: T015, T013
- **Estimate**: 1 hour

### T017: Generate changelog for interactive mode [US1]
- **File**: `src/bpkit_cli/commands/decompose.py` (changelog generation)
- **Story**: US1
- **Action**: Create changelog entry at `.specify/changelog/YYYY-MM-DD-decompose-v1.0.0.md`, document mode=interactive, sections processed, files generated, traceability links (FR-011)
- **Dependencies**: T016
- **Estimate**: 30 min

### T018: Display Rich-formatted summary [US1]
- **File**: `src/bpkit_cli/commands/decompose.py` (output formatting)
- **Story**: US1
- **Action**: Display section-by-section progress, principle extraction counts, feature detection results, final summary table with file paths and versions (FR-020), color-coded status (green/yellow/red)
- **Dependencies**: T016
- **Estimate**: 45 min

### T019: Integration test - Interactive mode [US1]
- **File**: `tests/integration/test_decompose_interactive.py`
- **Story**: US1
- **Action**: Simulate interactive Q&A (mock Rich prompts), verify pitch-deck.md created, verify 4 strategic + 5-10 feature constitutions, validate all traceability links with `/bp.analyze`, assert SC-005 (<15 min total time)
- **Dependencies**: T014-T018
- **Estimate**: 1 hour

**Checkpoint**: ✅ User Story 1 complete. Interactive mode fully functional and tested.

---

## Phase 4: User Story 2 - Markdown Pitch Deck Decomposition (P1)

**Goal**: Decompose existing markdown pitch deck into constitutions.

**Independent Test**: Create sample pitch-deck.md, run `bpkit decompose --from-file pitch-deck.md`, verify constitutions generated.

### T020: Implement markdown file parsing [US2]
- **File**: `src/bpkit_cli/commands/decompose.py` (from-file mode)
- **Story**: US2
- **Action**: Read markdown file from user-provided path, parse 10 Sequoia sections using SequoiaParser, detect missing sections (warn), handle extra sections (include but don't map), copy to `.specify/deck/pitch-deck.md` (FR-008)
- **Dependencies**: T007
- **Estimate**: 1 hour

### T021: Preserve markdown formatting [US2]
- **File**: `src/bpkit_cli/core/sequoia_parser.py` (formatting preservation)
- **Story**: US2
- **Action**: Extend parser to preserve inline formatting (bold, italic, lists, links) when extracting section content, pass through to generated constitutions (FR-014)
- **Dependencies**: T020
- **Estimate**: 45 min

### T022: Decompose markdown pitch deck [US2]
- **File**: `src/bpkit_cli/commands/decompose.py` (from-file mode)
- **Story**: US2
- **Action**: Reuse decomposition pipeline from T016 (PrincipleExtractor → FeatureDetector → ConstitutionGenerator), generate constitutions, create changelog with mode=from-file
- **Dependencies**: T020, T013
- **Estimate**: 30 min

### T023: Integration test - Markdown mode [US2]
- **File**: `tests/integration/test_decompose_file.py`
- **Story**: US2
- **Action**: Create test pitch-deck.md (AirBnB example), run decompose --from-file, verify 4 strategic + 7 feature constitutions, validate formatting preserved, assert SC-001 (<2 min), run `/bp.analyze` to validate links
- **Dependencies**: T020-T022
- **Estimate**: 1 hour

**Checkpoint**: ✅ User Story 2 complete. Markdown mode fully functional and tested.

---

## Phase 5: User Story 3 - PDF Pitch Deck Extraction (P2)

**Goal**: Extract text from PDF pitch deck, decompose into constitutions.

**Independent Test**: Run `bpkit decompose --from-pdf deck.pdf`, verify extraction quality, check constitutions.

### T024: Implement PDF extraction workflow [US3]
- **File**: `src/bpkit_cli/commands/decompose.py` (from-pdf mode)
- **Story**: US3
- **Action**: Load PDF file with PDFExtractor, extract text with section boundary detection, report extraction confidence, warn if <85% (SC-006), mark uncertain boundaries with [NEEDS REVIEW] (FR-015)
- **Dependencies**: T012
- **Estimate**: 1 hour

### T025: Generate markdown from PDF extraction [US3]
- **File**: `src/bpkit_cli/commands/decompose.py` (from-pdf mode)
- **Story**: US3
- **Action**: Convert extracted text to markdown format with h2 section headings, handle complex layouts (multi-column), report extraction artifacts, save to `.specify/deck/pitch-deck.md`
- **Dependencies**: T024
- **Estimate**: 1 hour

### T026: Decompose PDF-extracted pitch deck [US3]
- **File**: `src/bpkit_cli/commands/decompose.py` (from-pdf mode)
- **Story**: US3
- **Action**: Reuse decomposition pipeline from T016/T022, continue identically to markdown mode after extraction, create changelog with mode=from-pdf, include extraction confidence in changelog
- **Dependencies**: T025, T013
- **Estimate**: 30 min

### T027: Integration test - PDF mode [US3]
- **File**: `tests/integration/test_decompose_pdf.py`
- **Story**: US3
- **Action**: Use real-business-case-template-airbnb.pdf, run decompose --from-pdf, verify extraction confidence ≥85%, verify constitutions generated, assert SC-006, validate links
- **Dependencies**: T024-T026
- **Estimate**: 1 hour

**Checkpoint**: ✅ User Story 3 complete. PDF mode fully functional and tested.

---

## Phase 6: User Story 4 - Traceability Link Validation (P1)

**Goal**: Validate bidirectional traceability from pitch deck to constitutions.

**Independent Test**: Run decompose, then `/bp.analyze`, verify all links valid.

### T028: Integrate with Feature 002 link validator [US4]
- **File**: `src/bpkit_cli/commands/decompose.py` (validation)
- **Story**: US4
- **Action**: Import link_validator.py from Feature 002, call validate_all_links_async() on generated constitutions after decomposition, report any broken links (FR-012)
- **Dependencies**: T016, T022, T026
- **Estimate**: 45 min

### T029: Validate Source links (strategic constitutions) [US4]
- **File**: `src/bpkit_cli/core/constitution_generator.py` (link generation)
- **Story**: US4
- **Action**: Ensure all strategic principles include `**Source**: [pitch-deck.md#section-id]` links, validate section_id exists in pitch deck, generate link in correct format (FR-005)
- **Dependencies**: T013
- **Estimate**: 30 min

### T030: Validate Upstream links (feature constitutions) [US4]
- **File**: `src/bpkit_cli/core/constitution_generator.py` (link generation)
- **Story**: US4
- **Action**: Ensure all feature constitutions include `**Upstream**: [strategic-constitution.md#principle-id]` links to ≥1 strategic constitution, validate principle_id exists, generate link in correct format (FR-005)
- **Dependencies**: T013
- **Estimate**: 30 min

### T031: Impact analysis on pitch deck edits [US4]
- **File**: `src/bpkit_cli/core/impact_analyzer.py`
- **Story**: US4
- **Action**: Create ImpactAnalyzer class, identify downstream principles when pitch deck section edited (e.g., "Problem" → 5 affected principles), report in analysis output
- **Dependencies**: T028
- **Estimate**: 1 hour

### T032: Integration test - Traceability [US4]
- **File**: `tests/integration/test_traceability.py`
- **Story**: US4
- **Action**: Run decompose (any mode), validate all Source and Upstream links, test impact analysis (edit pitch deck section, verify affected principles reported), assert SC-003 (zero broken links)
- **Dependencies**: T028-T031
- **Estimate**: 1 hour

**Checkpoint**: ✅ User Story 4 complete. Traceability validation fully functional and tested.

---

## Phase 7: User Story 5 - Constitutional Versioning and Changelog (P2)

**Goal**: Track version history and changelog for business evolution.

**Independent Test**: Run decompose, edit pitch deck, re-run, verify version bumps and changelog.

### T033: Implement version bump logic [US5]
- **File**: `src/bpkit_cli/commands/decompose.py` (re-decomposition)
- **Story**: US5
- **Action**: Detect existing pitch-deck.md version, compare content, bump MINOR if new content added (FR-006), bump MAJOR if principles removed with downstream refs, bump PATCH if metadata only
- **Dependencies**: T001, Feature 002 version_tracker.py
- **Estimate**: 1 hour

### T034: Detect manual edits and prompt [US5]
- **File**: `src/bpkit_cli/commands/decompose.py` (re-decomposition)
- **Story**: US5
- **Action**: Detect existing constitution files, check if manually edited, prompt user: overwrite/skip/diff (FR-018), default=skip, create backup at `.specify/backups/` if overwrite chosen
- **Dependencies**: T033
- **Estimate**: 1 hour

### T035: Flag downstream constitutions for review [US5]
- **File**: `src/bpkit_cli/commands/decompose.py` (re-decomposition)
- **Story**: US5
- **Action**: When strategic constitution regenerated, identify all feature constitutions with Upstream links to changed principles, add to changelog "Features requiring review: 004-booking, 005-payment"
- **Dependencies**: T033, T031
- **Estimate**: 45 min

### T036: Generate changelog with version deltas [US5]
- **File**: `src/bpkit_cli/commands/decompose.py` (changelog)
- **Story**: US5
- **Action**: Create changelog entry documenting: which sections changed, which constitutions regenerated, new links added, version bump rationale (MAJOR/MINOR/PATCH) (FR-011)
- **Dependencies**: T033, T035
- **Estimate**: 1 hour

### T037: Integration test - Versioning [US5]
- **File**: `tests/integration/test_versioning.py`
- **Story**: US5
- **Action**: Run initial decompose (v1.0.0), edit pitch deck Problem section, re-decompose (expect v1.1.0), verify company-constitution version bumped, verify changelog documents change, assert SC-007 (correct version bump rules)
- **Dependencies**: T033-T036
- **Estimate**: 1 hour

**Checkpoint**: ✅ User Story 5 complete. Versioning and changelog fully functional and tested.

---

## Phase 8: Polish & Integration

### T038: Implement dry-run mode [P]
- **File**: `src/bpkit_cli/commands/decompose.py` (dry-run flag)
- **Story**: Polish
- **Action**: Add --dry-run flag, parse pitch deck and extract principles, display what would be generated (file paths, counts), do NOT write files or create changelog (FR-019)
- **Dependencies**: T001
- **Estimate**: 45 min

### T039: Implement edge case handling [P]
- **File**: `src/bpkit_cli/commands/decompose.py` (edge cases)
- **Story**: Polish
- **Action**: Handle duplicate section names (append -2, -3, warn), empty sections ([TODO] marker), 20+ features (limit to 10, warn), PDF extraction failures (suggest alternatives), fuzzy section matching
- **Dependencies**: T007, T009, T012
- **Estimate**: 1.5 hours

### T040: Create slash command documentation [P]
- **File**: `.claude/commands/bp.decompose.md`
- **Story**: Polish
- **Action**: Write comprehensive slash command doc with usage examples, all 3 modes, common scenarios, troubleshooting, integration with Speckit workflow
- **Dependencies**: T001-T037
- **Estimate**: 1 hour

### T041: Create pitch deck template for init [P]
- **File**: `.specify/deck/pitch-deck-template.md`
- **Story**: Polish
- **Action**: Create empty Sequoia template with 10 section headings + descriptions, used by `bpkit init` to scaffold new projects
- **Dependencies**: T002
- **Estimate**: 30 min

### T042: Update README with decompose examples [P]
- **File**: `README.md`
- **Story**: Polish
- **Action**: Add "Decomposition" section to README with quickstart examples for all 3 modes, AirBnB walkthrough, link to full documentation
- **Dependencies**: T001-T037
- **Estimate**: 45 min

### T043: End-to-end test - AirBnB example (SC-012) [P]
- **File**: `tests/integration/test_airbnb_e2e.py`
- **Story**: Polish
- **Action**: Use real-business-case-template-airbnb.pdf, extract text, decompose, verify 4 strategic + 7 feature constitutions, validate all links, assert accuracy ≥70% (SC-004), assert all SC-* criteria met
- **Dependencies**: T027, T032
- **Estimate**: 1.5 hours

### T044: Performance benchmarking
- **File**: `tests/performance/test_decompose_performance.py`
- **Story**: Polish
- **Action**: Benchmark decomposition time for 10-section pitch deck (assert <2 min for file/PDF mode per SC-001), benchmark interactive mode (assert <15 min per SC-005), validate principle extraction <100ms
- **Dependencies**: T001-T037
- **Estimate**: 1 hour

### T045: Final integration with Feature 002 Quality Commands
- **File**: `tests/integration/test_quality_workflow.py`
- **Story**: Polish
- **Action**: Test full workflow: decompose → clarify → analyze → checklist, verify constitutions pass quality validation (SC-011), verify 80% strategic checklist completion, 70% feature completion
- **Dependencies**: T001-T037, Feature 002 commands
- **Estimate**: 1 hour

**Checkpoint**: ✅ All tasks complete. Feature 003 ready for production.

---

## Dependencies Graph

```
Phase 1 (Setup): T001-T006 [All parallel]
    ↓
Phase 2 (Foundational): T007-T013 [Partial parallelization]
    ↓
Phase 3 (US1 - Interactive): T014-T019 [Sequential within phase]
    ↓
Phase 4 (US2 - Markdown): T020-T023 [Sequential within phase]
    ↓
Phase 5 (US3 - PDF): T024-T027 [Sequential within phase]
    ↓
Phase 6 (US4 - Traceability): T028-T032 [Partial parallelization]
    ↓
Phase 7 (US5 - Versioning): T033-T037 [Sequential within phase]
    ↓
Phase 8 (Polish): T038-T045 [Parallel opportunities]
```

**Critical Path**: T001 → T002 → T007 → T008 → T013 → T016 → T028 → T033 → T043

**Parallel Execution Opportunities**:
- Phase 1: All setup tasks (T001-T006) can run in parallel
- Phase 2: T007 [P] T012 (different files), T008-T011 after T007 completes
- Phase 8: T038 [P] T039 [P] T040 [P] T041 [P] T042 (different files)

---

## Task Summary by User Story

| User Story | Priority | Tasks | Estimate | Independent Test Criteria |
|------------|----------|-------|----------|---------------------------|
| **Setup** | - | T001-T006 | 2.5 hours | Models, templates, command entry point created |
| **Foundational** | - | T007-T013 | 12.5 hours | All extraction/generation logic functional |
| **US1: Interactive** | P1 | T014-T019 | 5.75 hours | Run --interactive, answer 10 questions, verify 4 strategic + N feature constitutions, links valid |
| **US2: Markdown** | P1 | T020-T023 | 3.25 hours | Create sample pitch-deck.md, run --from-file, verify constitutions, formatting preserved |
| **US3: PDF** | P2 | T024-T027 | 3.5 hours | Run --from-pdf on AirBnB PDF, verify extraction ≥85%, verify constitutions |
| **US4: Traceability** | P1 | T028-T032 | 3.75 hours | Run decompose + analyze, verify all links valid, test impact analysis |
| **US5: Versioning** | P2 | T033-T037 | 4.75 hours | Run decompose, edit deck, re-decompose, verify version bump + changelog |
| **Polish** | - | T038-T045 | 8.25 hours | All edge cases handled, documentation complete, AirBnB e2e test passes |
| **Total** | - | **45 tasks** | **44.25 hours** (~5-6 days) | All SC-* success criteria met |

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**Phase 1-4 (T001-T023)**: Interactive + Markdown modes with basic traceability
- **Delivers**: Core decomposition value (2 modes out of 3)
- **Time**: ~23.5 hours (~3 days)
- **User Stories**: US1 (Interactive - P1) + US2 (Markdown - P1) + partial US4 (basic links)

### Full Feature Scope
**Phase 1-8 (T001-T045)**: All user stories + polish
- **Delivers**: Complete feature with PDF mode, full traceability, versioning, edge cases
- **Time**: ~44.25 hours (~5-6 days)
- **User Stories**: All 5 user stories (US1-US5)

### Incremental Delivery Milestones
1. **Milestone 1** (T001-T019): Interactive mode functional - founders can create pitch decks from scratch
2. **Milestone 2** (T020-T023): Markdown mode functional - existing pitch decks can be decomposed
3. **Milestone 3** (T024-T027): PDF mode functional - presentation decks supported
4. **Milestone 4** (T028-T032): Full traceability validated - links guaranteed correct
5. **Milestone 5** (T033-T037): Versioning complete - business evolution tracked
6. **Milestone 6** (T038-T045): Production ready - all polish, edge cases, documentation

---

## Testing Strategy

**Test Distribution**:
- **Unit tests**: 13 tasks (T007-T013 core logic + selected polish tasks)
- **Integration tests**: 6 tasks (one per user story: T019, T023, T027, T032, T037, T043)
- **Performance tests**: 1 task (T044)
- **End-to-end tests**: 2 tasks (T043 AirBnB, T045 quality workflow)

**Test Coverage Targets**:
- Core extraction logic (principle, feature, entity, criteria): 90%+ unit test coverage
- User story acceptance scenarios: 100% integration test coverage
- Success criteria (SC-001 through SC-012): 100% validation coverage

**No TDD Approach**: Tests follow implementation (implementation tasks T014-T037, integration tests T019, T023, T027, T032, T037 come after)

---

## Risk Mitigation

**High-Risk Tasks**:
- **T008**: Principle extraction heuristics - 75-85% accuracy target (SC-004 requires ≥70%)
- **T009**: Feature detection - must identify 5-10 features reliably
- **T012**: PDF extraction - SC-006 requires ≥85% accuracy
- **T028-T030**: Traceability links - SC-003 requires zero broken links

**Mitigation Strategy**:
- Research phase validated heuristics against AirBnB example (11/11 principles extracted)
- Integration tests (T019, T023, T027, T032, T043) validate accuracy against success criteria
- If accuracy issues found, refine heuristics incrementally (pattern library extensible)

---

## Execution Instructions

### Quick Start (MVP - 3 days)
```bash
# Phase 1-2: Setup + Foundational
# Execute T001-T013 (models, templates, core extraction logic)

# Phase 3: Interactive Mode
# Execute T014-T019 (interactive Q&A, decomposition, integration test)

# Phase 4: Markdown Mode
# Execute T020-T023 (file parsing, decomposition, integration test)

# Test MVP
pytest tests/integration/test_decompose_interactive.py tests/integration/test_decompose_file.py
```

### Full Feature (5-6 days)
```bash
# Continue from MVP checkpoint

# Phase 5: PDF Mode
# Execute T024-T027 (PDF extraction, decomposition, integration test)

# Phase 6: Traceability
# Execute T028-T032 (link validation, impact analysis, integration test)

# Phase 7: Versioning
# Execute T033-T037 (version bump, manual edit detection, changelog, integration test)

# Phase 8: Polish
# Execute T038-T045 (dry-run, edge cases, docs, e2e tests)

# Validate all success criteria
pytest tests/integration/test_airbnb_e2e.py  # SC-012
pytest tests/performance/test_decompose_performance.py  # SC-001, SC-005, SC-006
```

---

## Success Criteria Validation

| Success Criterion | Validated By | Task |
|-------------------|--------------|------|
| SC-001: <2 min decomposition | Performance test | T044 |
| SC-002: 100% section mapping | Integration tests | T019, T023, T027 |
| SC-003: Zero broken links | Traceability test | T032 |
| SC-004: 70%+ feature accuracy | AirBnB e2e test | T043 |
| SC-005: <15 min interactive | Performance test | T044 |
| SC-006: 85%+ PDF accuracy | PDF integration test | T027 |
| SC-007: Correct version bumps | Versioning test | T037 |
| SC-008: Preserve manual edits | Re-decomposition test | T037 |
| SC-009: Complete changelog | Changelog validation | T036, T037 |
| SC-010: Dry-run accuracy | Dry-run test | T038 |
| SC-011: Quality validation | Quality workflow test | T045 |
| SC-012: AirBnB e2e success | AirBnB e2e test | T043 |

---

**Tasks File Complete**: 2025-10-11
**Ready For**: Implementation via `/speckit.implement`
