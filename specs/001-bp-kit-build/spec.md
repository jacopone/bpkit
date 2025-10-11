# Feature Specification: BP-Kit Init Command

**Feature Branch**: `001-bp-kit-build`
**Created**: 2025-10-10
**Status**: Draft
**Input**: User description: "BP-Kit: Build the bpkit init command that installs templates"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install BP-Kit in Existing Speckit Project (Priority: P1) 🎯 MVP

A developer has an existing Speckit project and wants to add BP-Kit templates to enable business plan decomposition.

**Why this priority**: This is the foundation for all BP-Kit functionality. Without the init command, users cannot use any other BP-Kit features.

**Independent Test**: Can be fully tested by running `bpkit init` in a Speckit project and verifying all templates and directories are created without conflicts.

**Acceptance Scenarios**:

1. **Given** I have a Speckit project (`.specify/` directory exists), **When** I run `bpkit init`, **Then** BP-Kit templates are added to `.specify/templates/` and `.claude/commands/` without overwriting existing Speckit files
2. **Given** I run `bpkit init` successfully, **When** I check the directory structure, **Then** I see `.specify/deck/`, `.specify/features/`, `.specify/changelog/` directories created
3. **Given** I run `bpkit init` successfully, **When** I list `.specify/templates/`, **Then** I see `pitch-deck-template.md`, `strategic-constitution-template.md`, and `feature-constitution-template.md`
4. **Given** I run `bpkit init` successfully, **When** I check `.claude/commands/`, **Then** I see `bp.decompose.md` and `bp.sync.md` slash commands
5. **Given** I run `bpkit init` in a directory that already has BP-Kit installed, **When** the command detects existing BP-Kit files, **Then** it prompts "BP-Kit already installed. Overwrite? (y/N)" and waits for user input (unless `--force` flag used, which skips prompt)

---

### User Story 2 - Bootstrap New Project with BP-Kit (Priority: P2)

A developer wants to start a new project with both Speckit and BP-Kit from scratch.

**Why this priority**: While less common than adding to existing projects, this provides a complete setup experience for new users.

**Independent Test**: Can be tested by running `bpkit init` in an empty directory and verifying complete project structure is created.

**Acceptance Scenarios**:

1. **Given** I'm in an empty directory (no `.specify/` folder), **When** I run `bpkit init my-startup`, **Then** both Speckit and BP-Kit structures are initialized with the project name
2. **Given** I initialize a new project with `bpkit init`, **When** the init completes, **Then** I see a welcome message with next steps (how to use `/bp.decompose`)
3. **Given** I initialize a new project, **When** I check git status, **Then** a `.gitignore` is present that excludes temporary files but includes templates

---

### User Story 3 - Verify Installation (Priority: P3)

A developer wants to verify BP-Kit is properly installed and configured.

**Why this priority**: Helpful for troubleshooting but not critical for basic functionality.

**Independent Test**: Can be tested by running `bpkit check` after initialization.

**Acceptance Scenarios**:

1. **Given** I have run `bpkit init`, **When** I run `bpkit check`, **Then** I see a report showing all required templates present, directory structure valid, and no conflicts with Speckit
2. **Given** BP-Kit templates are missing or corrupted, **When** I run `bpkit check`, **Then** I see specific error messages listing what needs to be fixed
3. **Given** I run `bpkit check` before initialization, **When** the command detects BP-Kit is not installed, **Then** it suggests running `bpkit init`

---

### Edge Cases

- What happens when user runs `bpkit init` in a directory that has Speckit templates but no `.specify/memory/constitution.md`? (Handle: Create missing constitution)
- What happens when `.specify/` directory exists but is empty? (Handle: Treat as fresh install)
- What happens when user has write permission issues? (Handle: Rollback any created files, fail with clear error message explaining permission requirements and which directory needs write access)
- What happens when Git is not initialized? (Handle: Prompt user "Git not detected. Create .gitignore for future use? (Y/n)" - respect user choice, continue installation either way)
- What happens when user already has custom templates with same names? (Handle: Prompt for backup or merge strategy)
- What happens when network connection fails during template download? (Handle: Rollback all created files, report which template failed to download, suggest checking network connection)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create `.specify/deck/`, `.specify/features/`, `.specify/changelog/`, and `.specify/scripts/bp/` directories if they don't exist
- **FR-002**: System MUST download `pitch-deck-template.md`, `strategic-constitution-template.md`, and `feature-constitution-template.md` from GitHub/CDN and save to `.specify/templates/` (requires network connection)
- **FR-003**: System MUST create `.claude/commands/bp.decompose.md` and `.claude/commands/bp.sync.md` slash command files
- **FR-004**: System MUST create bash utility scripts in `.specify/scripts/bp/` (bp-common.sh, decompose-setup.sh)
- **FR-005**: System MUST detect existing BP-Kit installation and prompt user "BP-Kit already installed. Overwrite? (y/N)" before overwriting unless `--force` flag is provided (which skips prompt and overwrites)
- **FR-006**: System MUST validate that installation completes without conflicts with Speckit files (no overwrites of `/speckit.*` commands or Speckit templates)
- **FR-007**: System MUST support `--project-name` option to set project name in templates
- **FR-008**: System MUST create or append to `.gitignore` entry for `.specify/deck/*.pdf` (pitch deck PDFs should not be committed by default). If no Git repository detected (no `.git/` folder), prompt user: "Git not detected. Create .gitignore for future use? (Y/n)"
- **FR-009**: System MUST display installation summary showing what was created and next steps
- **FR-010**: System MUST work both as CLI (`bpkit init`) and via package managers (`uvx --from git+https://... bpkit init`)
- **FR-011**: System MUST rollback all created files and directories if any installation step fails (network error, disk full, permission denied), returning system to pre-init state

### Key Entities

- **Template**: Markdown file with placeholders (e.g., `[PROJECT_NAME]`) that BP-Kit will fill during decomposition
  - Types: pitch-deck, strategic-constitution, feature-constitution
  - Location: `.specify/templates/`
  - Attributes: name, content, version

- **Directory Structure**: File system layout that BP-Kit expects
  - Directories: deck/, features/, changelog/, scripts/bp/
  - Purpose: Organize BP-Kit artifacts separately from Speckit artifacts
  - Constraints: Must not conflict with Speckit's directory structure

- **Slash Command**: AI agent command file in `.claude/commands/`
  - Types: bp.decompose, bp.sync
  - Format: Markdown file with execution instructions
  - Attributes: name, description, parameters, workflow

- **Installation State**: Metadata tracking what BP-Kit components are installed
  - Used by: `bpkit check` for validation
  - Stored: Implicitly (file existence checks)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can complete `bpkit init` in under 30 seconds (includes download time for templates)
- **SC-002**: Zero file conflicts with Speckit when installing in existing Speckit project (100% coexistence)
- **SC-003**: 95% of init attempts complete successfully on first try (measure: telemetry or user surveys)
- **SC-004**: Developer can run `/bp.decompose --interactive` immediately after `bpkit init` without additional setup
- **SC-005**: `bpkit check` reports "All systems ready" after successful `bpkit init`
- **SC-006**: Installation creates exactly 12 new files (3 templates, 2 slash commands, 2 bash scripts, 4 directories with README placeholders, 1 .gitignore entry)

### Assumptions

- Users have Python 3.11+ installed (required by constitution)
- Users have `uv` installed for package management (Speckit's installation method)
- Users have write permissions to the target directory
- Git is optional but recommended (BP-Kit will warn if not present)
- Users are familiar with command-line tools
- Network connection available during `bpkit init` for downloading templates from GitHub/CDN

## Dependencies

- **Python**: 3.11+ runtime
- **Typer**: CLI framework (installed as dependency)
- **Rich**: Console UI library (installed as dependency)
- **httpx[socks]**: HTTP client for downloading templates from GitHub/CDN (installed as dependency)
- **platformdirs**: For finding user config directories (installed as dependency)
- **Speckit**: Optional but recommended (BP-Kit enhances Speckit but can work standalone)

## Clarifications

### Session 2025-10-10

- Q: How should BP-Kit templates be distributed? → A: Downloaded on init - Templates fetched from GitHub/CDN during `bpkit init`, requires network connection at init time
- Q: What constitutes an "existing Speckit project" for detection purposes? → A: `.specify/` directory exists - Any project with `.specify/` folder is treated as Speckit project
- Q: How should BP-Kit handle partial installation failures? → A: Rollback on failure - Delete all created files/directories if any step fails, return to pre-init state
- Q: How should BP-Kit handle `.gitignore` creation when no Git repository exists? → A: Prompt user - Ask "Git not detected. Create .gitignore for future use? (Y/n)"
- Q: What format should the overwrite confirmation prompt use? → A: Simple Y/N - "BP-Kit already installed. Overwrite? (y/N)" as single yes/no choice

## Out of Scope (v1)

- Interactive prompts for customizing templates during init (user can edit templates manually after init)
- Automatic detection of project type (web/mobile/API) - templates are generic
- Integration with package managers other than `uv` (focus on Speckit's standard)
- Migration tool for converting existing project documentation to BP-Kit format
- Template versioning and auto-updates (v1 installs fixed template versions)
- Multi-language support (v1 is English only)
