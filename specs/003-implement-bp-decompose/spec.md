# Feature Specification: BP-Kit Build - Pitch Deck Decomposition

**Feature Branch**: `003-implement-bp-decompose`
**Created**: 2025-10-11
**Status**: Draft
**Input**: User description: "Implement /bp.decompose command to transform Sequoia Capital pitch decks into strategic constitutions (4 files: company, product, market, business) and feature constitutions (5-10 files for MVP features) with bidirectional traceability links. Support three modes: --interactive (Q&A), --from-file (markdown), and --from-pdf (extract). Generate all constitutions from pitch deck sections, maintain version control, create changelog entries, and preserve traceability from vision to executable specs."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Interactive Pitch Deck Creation (Priority: P1)

Founder with a business idea uses interactive Q&A mode to create a pitch deck and immediately decompose it into constitutional principles, enabling rapid transition from vision to MVP specs.

**Why this priority**: This is the primary workflow for founders starting from scratch. It delivers immediate value by capturing business vision in Sequoia's proven format and automatically generating structured specifications that AI agents can implement.

**Independent Test**: Can be fully tested by running `bpkit decompose --interactive`, answering Sequoia template questions (10 sections), and verifying that 4 strategic constitutions + feature constitutions are generated with valid traceability links. Delivers a complete constitutional system from zero prior artifacts.

**Acceptance Scenarios**:

1. **Given** fresh BP-Kit project with no pitch deck, **When** founder runs `bpkit decompose --interactive`, **Then** system prompts for Sequoia template sections sequentially (Company Purpose → Problem → Solution → Why Now → Market Size → Competition → Product → Business Model → Team → Financials)

2. **Given** founder answers all 10 section questions, **When** decomposition completes, **Then** system creates:
   - `.specify/deck/pitch-deck.md` (version 1.0.0) with all 10 sections
   - `.specify/memory/company-constitution.md` (principles from Company Purpose, Problem, Solution, Why Now)
   - `.specify/memory/product-constitution.md` (principles from Solution, Product sections)
   - `.specify/memory/market-constitution.md` (principles from Market Size, Competition)
   - `.specify/memory/business-constitution.md` (principles from Business Model, Financials, Team)
   - `.specify/features/001-*.md` through `.specify/features/00N-*.md` (5-10 feature constitutions derived from Product/Solution)

3. **Given** generated constitutions, **When** founder runs `bpkit analyze`, **Then** all traceability links validate successfully (pitch deck sections → strategic principles → feature principles)

4. **Given** interactive session in progress, **When** founder provides incomplete answer (e.g., "TBD" or blank), **Then** system accepts input but marks section with vagueness indicator for later clarification with `/bp.clarify`

5. **Given** interactive session completed, **When** founder reviews pitch deck, **Then** each section includes heading IDs (e.g., `#company-purpose`, `#problem`) for traceability linking

---

### User Story 2 - Markdown Pitch Deck Decomposition (Priority: P1)

Founder with existing markdown pitch deck (created manually or from previous session) decomposes it into constitutional principles, enabling reuse of prior work and integration with existing documentation workflows.

**Why this priority**: Many founders already have pitch decks in markdown format (from Obsidian, Notion exports, or manual creation). Supporting this mode allows BP-Kit to integrate into existing workflows without requiring rework.

**Independent Test**: Can be fully tested by creating a sample pitch deck markdown file following Sequoia template, running `bpkit decompose --from-file pitch-deck.md`, and verifying constitutional generation with traceability. Delivers value for users with existing documentation.

**Acceptance Scenarios**:

1. **Given** markdown file `my-pitch.md` with Sequoia sections (h2 headings: `## Company Purpose`, `## Problem`, etc.), **When** founder runs `bpkit decompose --from-file my-pitch.md`, **Then** system parses sections and generates 4 strategic + N feature constitutions

2. **Given** markdown pitch deck with custom filename and location, **When** founder runs `bpkit decompose --from-file ~/Documents/startup-pitch.md`, **Then** system copies content to `.specify/deck/pitch-deck.md` (canonical location) and proceeds with decomposition

3. **Given** markdown pitch deck missing required sections (e.g., no `## Business Model`), **When** decomposition runs, **Then** system generates warning listing missing sections and creates constitutions from available sections only

4. **Given** markdown pitch deck with extra custom sections (e.g., `## Go-To-Market Strategy`), **When** decomposition runs, **Then** system includes extra sections in pitch deck but does not map to strategic constitutions (requires manual mapping)

5. **Given** markdown pitch deck with inline links and formatting, **When** decomposition runs, **Then** system preserves markdown formatting in generated constitutions (bold, italic, lists, links)

---

### User Story 3 - PDF Pitch Deck Extraction and Decomposition (Priority: P2)

Founder with PDF pitch deck (from PowerPoint export, Keynote, or downloaded template) extracts text content and decomposes it into constitutional principles, enabling use of visual pitch decks created in presentation software.

**Why this priority**: Many founders create pitch decks in PowerPoint/Keynote for investor presentations. Supporting PDF extraction allows BP-Kit to work with these artifacts, though it's lower priority than interactive/markdown modes due to extraction complexity.

**Independent Test**: Can be fully tested by providing a PDF pitch deck (like AirBnB example), running `bpkit decompose --from-pdf deck.pdf`, verifying text extraction quality, and checking constitutional generation. Delivers value for founders with existing presentation decks.

**Acceptance Scenarios**:

1. **Given** PDF file `pitch-deck.pdf` with Sequoia sections, **When** founder runs `bpkit decompose --from-pdf pitch-deck.pdf`, **Then** system extracts text content, detects section boundaries (via heading font size/style heuristics), and generates markdown pitch deck

2. **Given** PDF with complex layouts (multi-column, images, charts), **When** text extraction runs, **Then** system extracts text in reading order and warns about potential extraction artifacts (e.g., "Extracted content may need manual review")

3. **Given** extracted markdown pitch deck from PDF, **When** founder reviews `.specify/deck/pitch-deck.md`, **Then** system marks uncertain section boundaries with `[NEEDS REVIEW]` comments for manual validation

4. **Given** PDF extraction complete, **When** decomposition proceeds, **Then** workflow continues identically to markdown mode (User Story 2) with constitutional generation

5. **Given** PDF file with embedded fonts or non-standard encoding, **When** extraction runs, **Then** system handles encoding issues gracefully and reports any unreadable sections

---

### User Story 4 - Traceability Link Validation (Priority: P1)

Developer or founder verifies bidirectional traceability from pitch deck vision through strategic principles to feature specifications, ensuring constitutional integrity and enabling impact analysis for changes.

**Why this priority**: Traceability is the core value proposition of BP-Kit - maintaining the closed feedback loop from vision to implementation. Without validated traceability, the constitutional system loses its integrity and usefulness.

**Independent Test**: Can be fully tested by running `/bp.decompose`, then `/bp.analyze`, and verifying that all generated links are valid. Delivers confidence that constitutional changes can be traced to business vision and vice versa.

**Acceptance Scenarios**:

1. **Given** freshly generated constitutions from decomposition, **When** founder runs `bpkit analyze`, **Then** system validates all `**Source**: [pitch-deck.md#section-id]` links resolve to actual pitch deck sections

2. **Given** feature constitution with `**Upstream**: [company-constitution.md#principle-3]` link, **When** validation runs, **Then** system confirms principle-3 exists in company constitution

3. **Given** pitch deck section `## Problem` linked from 5 strategic principles, **When** founder edits Problem section, **Then** system can identify downstream impact (5 affected principles) for manual review

4. **Given** strategic principle linked from 3 feature constitutions, **When** principle is deleted or renamed, **Then** `/bp.analyze` reports 3 broken links with suggested fixes

5. **Given** all constitutions generated, **When** founder runs `bpkit analyze --verbose`, **Then** system displays traceability graph showing pitch deck → strategic → feature relationships

---

### User Story 5 - Constitutional Versioning and Changelog (Priority: P2)

System tracks version history of pitch deck and constitutions as business evolves, enabling audit trail of strategic pivots and constitutional changes over time.

**Why this priority**: Startups pivot frequently. Version tracking enables founders to understand how their business vision evolved and provides context for constitutional changes, supporting the "learning loop" aspect of BP-Kit.

**Independent Test**: Can be fully tested by running `/bp.decompose`, editing pitch deck, re-running decomposition, and verifying version bumps and changelog entries. Delivers historical context for strategic evolution.

**Acceptance Scenarios**:

1. **Given** initial decomposition creates pitch-deck.md version 1.0.0, **When** founder edits Problem section and re-runs decomposition, **Then** pitch deck version bumps to 1.1.0 (MINOR) and company-constitution.md bumps accordingly

2. **Given** pitch deck version 1.1.0 and constitutions exist, **When** founder adds new Product feature and decomposes, **Then** new feature constitution is created with version 1.0.0 while existing constitutions reference pitch-deck v1.1.0

3. **Given** decomposition completes, **When** version bump occurs, **Then** changelog entry is created at `.specify/changelog/YYYY-MM-DD-decompose-vX.X.X.md` documenting:
   - Which pitch deck sections changed
   - Which constitutions were regenerated
   - New traceability links added
   - Version bump rationale (MAJOR/MINOR/PATCH)

4. **Given** strategic constitution regenerated from updated pitch deck, **When** version bumps, **Then** all downstream feature constitutions referencing that strategic constitution are flagged for review (via `/bp.analyze`)

5. **Given** multiple decomposition runs over time, **When** founder reviews `.specify/changelog/`, **Then** timeline of business evolution is visible (initial vision → pivot 1 → pivot 2)

---

### Edge Cases

- **What happens when pitch deck has duplicate section names?** System detects duplicates and generates unique heading IDs by appending `-2`, `-3`, etc. Warns user about ambiguous structure.

- **What happens when pitch deck section has no content?** System creates empty section in pitch deck with `[TODO]` marker and generates strategic constitution with placeholder principle pointing to empty section. `/bp.clarify` can later fill gaps.

- **What happens when Product section lists 20 features?** System generates maximum 10 feature constitutions (configurable) by prioritizing features mentioned first or using heuristics (frequency, emphasis). Warns user about truncation.

- **What happens when PDF extraction fails completely?** System reports extraction error, provides diagnostic info (e.g., "PDF may be image-based, requires OCR"), and suggests using `--interactive` or `--from-file` modes instead.

- **What happens when strategic constitution already exists with manual edits?** System detects existing file, prompts user for action: (1) overwrite with regenerated version, (2) skip regeneration and keep manual edits, or (3) create side-by-side diff for manual merge. Default: skip to preserve manual work.

- **What happens when pitch deck uses non-Sequoia section names?** System attempts fuzzy matching (e.g., "Value Proposition" → "Solution") and prompts user to confirm mappings. Unmatched sections are included in pitch deck but not mapped to strategic constitutions.

- **What happens when running decompose multiple times in succession?** System detects existing pitch-deck.md version, checks if content differs. If identical, skips regeneration. If different, performs version bump and documents delta in changelog.

- **What happens when feature constitution references non-existent principle?** Validation in User Story 4 catches this during `/bp.analyze`. Decomposition process itself should not create broken links, but if manual edits occur post-decomposition, validation flags issues.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse Sequoia pitch deck template with 10 canonical sections: Company Purpose, Problem, Solution, Why Now, Market Size, Competition, Product, Business Model, Team, Financials

- **FR-002**: System MUST support three decomposition modes: `--interactive` (Q&A), `--from-file <path>` (markdown parsing), `--from-pdf <path>` (PDF text extraction)

- **FR-003**: System MUST generate 4 strategic constitutions from pitch deck sections with the following mappings:
  - `company-constitution.md`: Company Purpose, Problem, Solution, Why Now
  - `product-constitution.md`: Solution, Product
  - `market-constitution.md`: Market Size, Competition
  - `business-constitution.md`: Business Model, Financials, Team

- **FR-004**: System MUST extract 5-10 feature constitutions from Product and Solution sections by identifying discrete product capabilities, use cases, or user-facing features mentioned in pitch deck content

- **FR-005**: System MUST create bidirectional traceability links:
  - Strategic constitutions include `**Source**: [pitch-deck.md#section-id]` links to pitch deck sections
  - Feature constitutions include `**Upstream**: [strategic-constitution.md#principle-id]` links to strategic principles
  - All links MUST use markdown heading ID syntax (e.g., `#company-purpose`, `#principle-1`)

- **FR-006**: System MUST assign semantic versions (MAJOR.MINOR.PATCH) to generated artifacts:
  - Initial decomposition: all files start at version 1.0.0
  - Re-decomposition with changed content: bump MINOR version (new principles added)
  - Breaking changes (removed principles referenced downstream): bump MAJOR version
  - Metadata-only changes: bump PATCH version

- **FR-007**: System MUST include YAML frontmatter in all generated files:
  ```yaml
  ---
  version: X.Y.Z
  type: strategic | feature
  created: YYYY-MM-DD
  updated: YYYY-MM-DD
  source: pitch-deck.md
  ---
  ```

- **FR-008**: System MUST create canonical pitch deck at `.specify/deck/pitch-deck.md` regardless of input mode (interactive/file/pdf), with all 10 Sequoia sections as h2 headings

- **FR-009**: System MUST create strategic constitutions at `.specify/memory/{company,product,market,business}-constitution.md` with principles extracted from mapped pitch deck sections

- **FR-010**: System MUST create feature constitutions at `.specify/features/###-feature-name.md` with sequential numbering (001, 002, ..., 010) and kebab-case naming derived from feature titles

- **FR-011**: System MUST generate changelog entry at `.specify/changelog/YYYY-MM-DD-decompose-v{version}.md` documenting:
  - Decomposition mode used (interactive/file/pdf)
  - Pitch deck sections processed
  - Strategic constitutions generated/updated
  - Feature constitutions generated
  - Traceability links created
  - Version bumps and rationale

- **FR-012**: System MUST validate generated traceability links using existing `/bp.analyze` command infrastructure (reuse link validator from Feature 002)

- **FR-013**: Interactive mode MUST present Sequoia section questions sequentially with:
  - Section name and description (from Sequoia template)
  - Suggested prompts/examples (e.g., for Market Size: "Calculate TAM, SAM, SOM")
  - Multi-line text input capability
  - Ability to skip sections (leaves section with `[TODO]` marker)

- **FR-014**: Markdown parsing MUST extract sections using h2 headings (`## Section Name`), preserve inline formatting (bold, italic, lists, links), and generate GitHub-style heading IDs for traceability

- **FR-015**: PDF extraction MUST use text extraction library (e.g., PyMuPDF/pymupdf4llm), detect section boundaries via font size/style heuristics, handle multi-column layouts in reading order, and report extraction confidence level

- **FR-016**: Feature extraction MUST parse Product/Solution sections for discrete capabilities using heuristics:
  - Bulleted/numbered lists of features
  - Sentences starting with action verbs (e.g., "Allow users to...", "Enable hosts to...")
  - Keywords: "feature", "capability", "use case", "workflow"
  - Maximum 10 features extracted (user-configurable limit)

- **FR-017**: System MUST detect and warn about incomplete pitch deck sections:
  - Empty sections (no content beyond heading)
  - Sections with placeholder markers (`[TBD]`, `[TODO]`, `[NEEDS DETAILS]`)
  - Missing required sections (fewer than 10 Sequoia sections found)
  - Suggests using `/bp.clarify` to resolve ambiguities

- **FR-018**: System MUST preserve existing manual edits during re-decomposition by:
  - Detecting existing constitution files
  - Prompting user: overwrite / skip / diff
  - Default behavior: skip (preserve manual work)
  - If overwrite chosen: create backup at `.specify/backups/YYYY-MM-DD-HH-MM-SS/`

- **FR-019**: System MUST support dry-run mode (`--dry-run`) that:
  - Parses pitch deck and extracts principles
  - Displays what would be generated (file paths, principle counts)
  - Does NOT write any files or create changelog entries
  - Useful for previewing decomposition before committing

- **FR-020**: System MUST display Rich-formatted progress output during decomposition:
  - Section-by-section progress (e.g., "Parsing Problem section...")
  - Principle extraction counts (e.g., "Extracted 3 principles from Company Purpose")
  - Feature detection results (e.g., "Identified 7 MVP features from Product section")
  - Final summary table showing all generated files with versions
  - Color-coded status (green=created, yellow=updated, red=errors)

### Key Entities

- **PitchDeck**: Markdown document at `.specify/deck/pitch-deck.md` containing 10 Sequoia sections (Company Purpose, Problem, Solution, Why Now, Market Size, Competition, Product, Business Model, Team, Financials). Each section is h2 heading with GitHub-style ID for linking. Includes YAML frontmatter with version, source mode (interactive/file/pdf), creation date.

- **PitchDeckSection**: Individual section within pitch deck (e.g., Problem, Solution). Contains heading ID, title, content (markdown formatted), position (1-10). Referenced by strategic constitutions via traceability links.

- **StrategicConstitution**: Markdown document at `.specify/memory/{company,product,market,business}-constitution.md` containing principles derived from pitch deck sections. Includes `**Source**` links to pitch deck sections, versioning metadata, principle hierarchy. Four types based on section mappings defined in FR-003.

- **FeatureConstitution**: Markdown document at `.specify/features/###-feature-name.md` containing user stories, entities, principles, success criteria for one MVP feature. Includes `**Upstream**` links to strategic constitutions, sequential numbering (001-010), feature priority. Derived from Product/Solution sections.

- **Principle**: Individual strategic or tactical guideline extracted from pitch deck content. Contains ID (e.g., `#principle-1`), title, description, traceability link to source. Strategic principles live in strategic constitutions, tactical principles in feature constitutions.

- **TraceabilityLink**: Markdown link connecting artifacts in the constitutional hierarchy:
  - Pitch deck section ← Strategic principle (`**Source**: [pitch-deck.md#problem]`)
  - Strategic principle ← Feature principle (`**Upstream**: [company-constitution.md#principle-2]`)
  - Format: `[link-text](relative-path#heading-id)`
  - Validated by `/bp.analyze` link validator

- **DecompositionMode**: Enum specifying how pitch deck content is obtained: INTERACTIVE (Q&A), FROM_FILE (markdown parsing), FROM_PDF (text extraction). Determines parsing strategy and user interaction model.

- **VersionMetadata**: Semantic version (MAJOR.MINOR.PATCH) with creation/update timestamps in YAML frontmatter. Tracks constitutional evolution over time. Bump rules: MAJOR=breaking changes, MINOR=new content, PATCH=metadata/formatting.

- **ChangelogEntry**: Markdown document at `.specify/changelog/YYYY-MM-DD-decompose-v{version}.md` documenting decomposition results. Contains mode used, sections processed, files generated/updated, version bumps, traceability links created. Provides audit trail for business evolution.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Decomposition completes in under 2 minutes for typical 10-section pitch deck in `--from-file` or `--from-pdf` mode (excluding user input time for interactive mode)

- **SC-002**: 100% of pitch deck sections are mapped to strategic constitutions according to FR-003 mappings (all 10 Sequoia sections represented in the 4 strategic constitutions)

- **SC-003**: All generated traceability links validate successfully when running `/bp.analyze` immediately after decomposition (zero broken links in fresh decomposition output)

- **SC-004**: Feature extraction identifies 5-10 MVP features from Product/Solution sections with minimum 70% accuracy (validated against manual review of same pitch deck by domain expert)

- **SC-005**: Interactive mode pitch deck creation completes in under 15 minutes for founder answering all 10 section questions (measured from command start to final file generation)

- **SC-006**: PDF extraction achieves minimum 85% text extraction accuracy for standard pitch deck PDFs (compared to manual transcription, measured on 10 sample decks)

- **SC-007**: Version bumping correctly increments MINOR version on re-decomposition when new principles added, and MAJOR version when principles removed that have downstream references (validated by test suite)

- **SC-008**: System preserves 100% of manual edits when re-decomposition runs in skip mode (default behavior) - no accidental overwrites of user-modified constitutions

- **SC-009**: Changelog entries contain all required information: mode, sections processed, files generated, version bumps, traceability links (validated by checklist review)

- **SC-010**: Dry-run mode (`--dry-run`) provides accurate preview matching actual file generation when dry-run flag is removed (validated by comparing dry-run output to real run results)

- **SC-011**: Generated constitutions pass `/bp.checklist` quality validation with minimum 80% checklist completion for strategic constitutions and 70% for feature constitutions (some items require manual completion like success metrics)

- **SC-012**: Integration test: AirBnB pitch deck example decomposes successfully into 4 strategic + 7 feature constitutions with all traceability links valid (end-to-end validation)
