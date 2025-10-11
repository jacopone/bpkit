# Tasks: BP-Kit Init Command

**Input**: Design documents from `/specs/001-bp-kit-build/`
**Prerequisites**: plan.md (tech stack, structure), spec.md (user stories), research.md (technical decisions), data-model.md (entities), contracts/ (API specs)

**Tests**: No test tasks included - not explicitly requested in feature specification

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Project Type**: Single CLI package (Python)
- **Source**: `src/bpkit_cli/` at repository root
- **Tests**: `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create core module directories: `src/bpkit_cli/commands/`, `src/bpkit_cli/core/`, `src/bpkit_cli/models/`
- [x] T002 Create test directories: `tests/unit/`, `tests/integration/`, `tests/contract/`
- [x] T003 [P] Update pyproject.toml with dependencies: tenacity (for retry logic), pytest, pytest-cov (dev dependencies already include httpx, typer, rich, pydantic, pyyaml per plan.md)
- [x] T004 [P] Create pytest configuration in `tests/conftest.py` with fixtures for temp directories and mock httpx responses

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core models and utilities that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 [P] Implement Template model in `src/bpkit_cli/models/template.py` (attributes: name, source_url, destination_path, content, type per data-model.md)
- [x] T006 [P] Implement Directory model in `src/bpkit_cli/models/directory.py` (attributes: path, exists_before_install, created_by_bpkit per data-model.md)
- [x] T007 [P] Implement InstallationState model in `src/bpkit_cli/models/install_state.py` (attributes: status, project_dir, files_created, dirs_created, conflicts per data-model.md)
- [x] T008 [P] Implement GitRepository model in `src/bpkit_cli/models/git_repository.py` (attributes: exists, gitignore_path, gitignore_exists per data-model.md)
- [x] T009 Implement atomic installation context manager in `src/bpkit_cli/core/installer.py` (InstallationRollback class with LIFO tracking per research.md)
- [x] T010 [P] Implement template download function with retry logic in `src/bpkit_cli/core/templates.py` (use httpx + tenacity, 3 retries with exponential backoff per research.md)
- [x] T011 [P] Implement placeholder replacement function in `src/bpkit_cli/core/templates.py` (simple str.replace for [PROJECT_NAME] per research.md)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Install BP-Kit in Existing Speckit Project (Priority: P1) 🎯 MVP

**Goal**: Install BP-Kit templates and directories in existing Speckit project without conflicts, completing in <30 seconds

**Independent Test**: Run `bpkit init` in a directory with existing `.specify/` folder, verify all 12 files created, no Speckit files overwritten, check command reports success

### Implementation for User Story 1

- [x] T012 [P] [US1] Implement Speckit detection function in `src/bpkit_cli/core/validation.py` (check for `.specify/` directory existence per clarification Q2)
- [x] T013 [P] [US1] Implement BP-Kit detection function in `src/bpkit_cli/core/validation.py` (check for BP-Kit markers: `.specify/deck/`, pitch-deck-template.md, bp.decompose.md per data-model.md)
- [x] T014 [P] [US1] Implement Speckit conflict validation function in `src/bpkit_cli/core/validation.py` (ensure no overwrites of `/speckit.*` commands or Speckit templates per FR-006)
- [x] T015 [US1] Implement overwrite prompt function in `src/bpkit_cli/commands/init.py` (use typer.confirm with "BP-Kit already installed. Overwrite? (y/N)" per clarification Q5 and research.md)
- [x] T016 [US1] Implement directory creation logic in `src/bpkit_cli/commands/init.py` (create `.specify/deck/`, `.specify/features/`, `.specify/changelog/`, `.specify/scripts/bp/` with tracking per FR-001)
- [x] T017 [US1] Implement template installation function in `src/bpkit_cli/commands/init.py` (download 7 templates from GitHub raw URLs per contracts/github-raw-api.yaml, save to destinations per FR-002, FR-003, FR-004)
- [x] T018 [US1] Implement init command main logic for US1 path in `src/bpkit_cli/commands/init.py` function `run_init()` (orchestrate: detect Speckit, check conflicts, prompt if needed, install with rollback, handle --force flag per FR-005, FR-010, FR-011)
- [x] T019 [US1] Implement installation summary output in `src/bpkit_cli/commands/init.py` (display created directories/files, next steps per FR-009 and contracts/cli-interface.md success output)
- [ ] T020 [US1] Create integration test `tests/integration/test_init_existing.py` (test acceptance scenarios 1-5 from spec.md US1)

**Checkpoint**: At this point, User Story 1 should be fully functional - can install BP-Kit in existing Speckit projects

---

## Phase 4: User Story 2 - Bootstrap New Project with BP-Kit (Priority: P2)

**Goal**: Create both Speckit and BP-Kit structures from scratch with project name replacement and .gitignore handling

**Independent Test**: Run `bpkit init my-project` in empty directory, verify complete structure created, `[PROJECT_NAME]` replaced with "my-project", .gitignore present

### Implementation for User Story 2

- [x] T021 [P] [US2] Implement Git detection function in `src/bpkit_cli/core/validation.py` (check for `.git/` directory per GitRepository model in data-model.md)
- [x] T022 [US2] Implement .gitignore prompt function in `src/bpkit_cli/commands/init.py` (use typer.confirm with "Git not detected. Create .gitignore for future use? (Y/n)" per clarification Q4)
- [x] T023 [US2] Implement .gitignore creation/append function in `src/bpkit_cli/commands/init.py` (create or append `.specify/deck/*.pdf` entry per FR-008, handle existing .gitignore)
- [x] T024 [US2] Extend init command for bootstrap path in `src/bpkit_cli/commands/init.py` (detect empty directory, create `.specify/` structure, handle project_name argument per FR-007, use placeholder replacement from T011)
- [x] T025 [US2] Implement welcome message for new projects in `src/bpkit_cli/commands/init.py` (display next steps: create pitch deck, run /bp.decompose per spec.md US2 acceptance scenario 2)
- [ ] T026 [US2] Create integration test `tests/integration/test_init_fresh.py` (test acceptance scenarios 1-3 from spec.md US2)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - can install in existing projects OR bootstrap new ones

---

## Phase 5: User Story 3 - Verify Installation (Priority: P3)

**Goal**: Provide `bpkit check` command to validate BP-Kit installation and report status

**Independent Test**: Run `bpkit check` after init, verify report shows all components present; run before init, verify suggestion to run `bpkit init`

### Implementation for User Story 3

- [x] T027 [P] [US3] Implement directory structure validation in `src/bpkit_cli/commands/check.py` function `check_directories()` (verify `.specify/deck/`, `.specify/features/`, `.specify/changelog/`, `.specify/scripts/bp/` exist)
- [x] T028 [P] [US3] Implement template presence validation in `src/bpkit_cli/commands/check.py` function `check_templates()` (verify 3 templates in `.specify/templates/`: pitch-deck, strategic-constitution, feature-constitution)
- [x] T029 [P] [US3] Implement slash command validation in `src/bpkit_cli/commands/check.py` function `check_slash_commands()` (verify bp.decompose.md and bp.sync.md in `.claude/commands/`)
- [x] T030 [P] [US3] Implement bash script validation in `src/bpkit_cli/commands/check.py` function `check_bash_scripts()` (verify bp-common.sh and decompose-setup.sh in `.specify/scripts/bp/`)
- [x] T031 [US3] Implement check command main logic in `src/bpkit_cli/commands/check.py` function `run_check()` (orchestrate all validations, determine overall status)
- [x] T032 [US3] Implement check report output in `src/bpkit_cli/commands/check.py` (display validation results with ✓/✗ symbols per contracts/cli-interface.md, show "All systems ready" or error messages per spec.md US3)
- [ ] T033 [US3] Create integration test `tests/integration/test_check.py` (test acceptance scenarios 1-3 from spec.md US3: check after init, check with missing files, check before init)

**Checkpoint**: All user stories should now be independently functional - init installs, check verifies

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, robustness, and final improvements that affect multiple user stories

- [x] T034 [P] Add comprehensive network error handling in `src/bpkit_cli/core/templates.py` (catch httpx exceptions: NetworkError, Timeout, HTTPStatusError; display user-friendly messages per contracts/cli-interface.md error outputs)
- [x] T035 [P] Add permission denied error handling in `src/bpkit_cli/commands/init.py` (catch PermissionError, OSError during directory/file creation; trigger rollback and display helpful message per edge case handling in spec.md)
- [x] T036 [US1+US2] Implement --force flag handling in `src/bpkit_cli/commands/init.py` (skip all prompts, assume yes to overwrite and .gitignore per research.md and contracts/cli-interface.md)
- [x] T037 [US1+US2] Add progress indicators for downloads in `src/bpkit_cli/commands/init.py` (use Rich Progress bar to show "Downloading template X of 7..." per contracts/cli-interface.md performance contract)
- [x] T038 Create unit tests for rollback mechanism in `tests/unit/test_installer.py` (test LIFO deletion, partial state cleanup, only-delete-created-paths safety per research.md rollback pattern)
- [x] T039 Create unit tests for template download retry in `tests/unit/test_templates.py` (test 3-retry logic, exponential backoff, network failure handling per research.md)
- [ ] T040 [P] Create contract test for GitHub raw API in `tests/contract/test_template_downloads.py` (verify actual GitHub URLs return 200, validate response content is markdown/bash per contracts/github-raw-api.yaml)
- [x] T041 Create integration test for overwrite behavior in `tests/integration/test_init_overwrite.py` (test prompt behavior, --force flag, rollback on user decline per spec.md US1 acceptance scenario 5)
- [x] T042 Create integration test for full workflow in `tests/integration/test_full_workflow.py` (init → check reports success → re-init with --force → check still reports success)
- [x] T043 [P] Update README.md with installation section (add `uv tool install` command, link to quickstart.md per plan.md)
- [x] T044 [P] Validate implementation readiness (all core features implemented and documented)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion
  - User Story 1 (P1) can start after Foundational - No dependencies on other stories
  - User Story 2 (P2) depends on User Story 1 (extends init command) - Sequential after US1
  - User Story 3 (P3) is independent - Can start after Foundational in parallel with US1/US2
- **Polish (Phase 6)**: Depends on desired user stories being complete (minimally US1 for MVP)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - **INDEPENDENT**
- **User Story 2 (P2)**: Depends on User Story 1 completion - Extends init command with bootstrap path
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - **INDEPENDENT** (just reads state)

### Within Each User Story

**User Story 1**:
- T012-T014 (validation functions) can run in parallel [P]
- T015-T017 sequential (build on each other)
- T018 depends on T015-T017 (orchestrates them)
- T019 depends on T018 (displays results)
- T020 after all implementation (integration test)

**User Story 2**:
- T021-T023 can run in parallel [P]
- T024 depends on US1 T018 (extends run_init)
- T025-T026 sequential after T024

**User Story 3**:
- T027-T030 can run in parallel [P] (different validation functions)
- T031 depends on T027-T030 (orchestrates)
- T032-T033 sequential after T031

**Phase 6 Polish**:
- T034-T035 can run in parallel [P] (different error types)
- T036-T037 depend on init command being functional (US1/US2)
- T038-T040 can run in parallel [P] (different test files)
- T041-T042 depend on full implementation
- T043-T044 can run in parallel [P] (documentation tasks)

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003 and T004 can run in parallel [P]

**Phase 2 (Foundational)**:
- T005-T008 (all model files) can run in parallel [P]
- T010-T011 can run in parallel [P] after models exist

**Phase 3 (User Story 1)**:
- T012-T014 can run in parallel [P]

**Phase 5 (User Story 3)**:
- T027-T030 can run in parallel [P]

**Phase 6 (Polish)**:
- T034-T035 can run in parallel [P]
- T038-T040 can run in parallel [P]
- T043-T044 can run in parallel [P]

**Cross-Story Parallelism**:
- User Story 3 (Phase 5) can be developed in parallel with User Story 1 (Phase 3) since US3 is independent

---

## Parallel Example: Foundational Phase

```bash
# Launch all model files together (Phase 2):
Task: "Implement Template model in src/bpkit_cli/models/template.py"
Task: "Implement Directory model in src/bpkit_cli/models/directory.py"
Task: "Implement InstallationState model in src/bpkit_cli/models/install_state.py"
Task: "Implement GitRepository model in src/bpkit_cli/models/git_repository.py"

# Then launch template utilities together:
Task: "Implement template download function with retry in src/bpkit_cli/core/templates.py"
Task: "Implement placeholder replacement in src/bpkit_cli/core/templates.py"
```

## Parallel Example: User Story 1

```bash
# Launch all validation functions together:
Task: "Implement Speckit detection in src/bpkit_cli/core/validation.py"
Task: "Implement BP-Kit detection in src/bpkit_cli/core/validation.py"
Task: "Implement conflict validation in src/bpkit_cli/core/validation.py"
```

## Parallel Example: User Story 3

```bash
# Launch all check functions together:
Task: "Implement directory structure validation in src/bpkit_cli/commands/check.py"
Task: "Implement template presence validation in src/bpkit_cli/commands/check.py"
Task: "Implement slash command validation in src/bpkit_cli/commands/check.py"
Task: "Implement Speckit conflict check in src/bpkit_cli/commands/check.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T011) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 (T012-T020)
4. **STOP and VALIDATE**: Test `bpkit init` in existing Speckit project, verify all 12 files created, <30 seconds, zero conflicts
5. Optionally add Phase 6 essential polish (T034-T037 for error handling)
6. Deploy/demo MVP

**MVP Scope**: User Story 1 provides core value - installing BP-Kit in existing Speckit projects (the most common use case per spec.md)

### Incremental Delivery

1. **Milestone 1**: Setup + Foundational → Core infrastructure ready
2. **Milestone 2**: + User Story 1 → Install in existing projects (MVP!) ← **RECOMMENDED FIRST RELEASE**
3. **Milestone 3**: + User Story 2 → Bootstrap new projects
4. **Milestone 4**: + User Story 3 → Verify installations
5. **Milestone 5**: + Polish → Production-ready (error handling, tests, docs)

Each milestone adds value without breaking previous functionality.

### Parallel Team Strategy

With 2 developers:

1. **Together**: Complete Setup (Phase 1) + Foundational (Phase 2)
2. **Developer A**: User Story 1 (Phase 3) - Priority 1
3. **Developer B**: User Story 3 (Phase 5) - Independent, can start after Foundational
4. **Together**: User Story 2 (Phase 4) - Depends on US1, sequential
5. **Divide**: Polish tasks (Phase 6) - Assign T034-T037 to Dev A, T038-T044 to Dev B

With 1 developer (sequential):

1. Phase 1 (4 tasks, ~30 min)
2. Phase 2 (7 tasks, ~2 hours) - CRITICAL PATH
3. Phase 3 (9 tasks, ~3 hours) - MVP COMPLETE after this
4. Phase 4 (6 tasks, ~1.5 hours)
5. Phase 5 (7 tasks, ~1.5 hours)
6. Phase 6 (11 tasks, ~2 hours)

**Total Estimated Time**: 10-12 hours for full implementation

---

## Notes

- [P] tasks = different files/functions, can run in parallel
- [Story] label (US1, US2, US3) maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group (e.g., all models, all validation functions)
- Stop at any checkpoint to validate story independently
- Constitution Check already passed in plan.md - all tasks align with 5 core principles
- Performance target: <30 seconds (SC-001) achievable with async downloads or sequential (research.md estimates 3-8s typical)
- Avoid: Cross-story dependencies that break independence, same-file parallel tasks

## Success Criteria Mapping

Tasks map to success criteria from spec.md:

- **SC-001** (< 30s completion): T010 (download optimization), T037 (progress indicators)
- **SC-002** (Zero conflicts): T014 (conflict validation), enforced by FR-006 throughout
- **SC-003** (95% success rate): T034-T035 (error handling), T038-T039 (retry logic tests)
- **SC-004** (Ready for /bp.decompose): T017 (installs slash commands)
- **SC-005** (Check reports ready): T027-T032 (check command implementation)
- **SC-006** (12 files created): T017 (template installation), validated by T020, T026, T033 (integration tests)
