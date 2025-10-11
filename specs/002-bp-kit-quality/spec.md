# Feature Specification: BP-Kit Quality Commands

**Feature Branch**: `002-bp-kit-quality`
**Created**: 2025-10-10
**Status**: Draft
**Input**: User description: "BP-Kit Quality Commands - Optional workflow commands to improve constitution quality similar to Speckit's clarify/analyze/checklist commands"

## User Scenarios & Testing

### User Story 1 - Clarify Ambiguous Pitch Deck Sections (Priority: P1)

A founder has created their pitch deck but realizes some sections are vague or incomplete. Before running `/bp.decompose`, they want to identify and resolve ambiguities to ensure high-quality constitutions are generated.

**Why this priority**: Prevents "garbage in, garbage out" - unclear pitch decks lead to weak constitutions. This is the earliest intervention point in the BP-Kit workflow, making it the highest leverage for quality.

**Independent Test**: Run `/bp.clarify` on a pitch deck with incomplete sections (e.g., missing competitive advantage, vague market size). System identifies 3-5 critical questions, user answers them interactively, and pitch deck is updated with clarifications. Can be tested without running full decomposition.

**Acceptance Scenarios**:

1. **Given** a pitch deck with vague "Competition" section, **When** user runs `/bp.clarify`, **Then** system asks "Who are your top 3 competitors and what is your specific advantage over each?"
2. **Given** pitch deck missing unit economics, **When** user runs `/bp.clarify --section=business-model`, **Then** system asks targeted questions about CAC, LTV, margins
3. **Given** a complete, well-defined pitch deck, **When** user runs `/bp.clarify`, **Then** system reports "No clarifications needed - deck ready for decomposition"
4. **Given** clarification questions generated, **When** user provides answers, **Then** pitch deck sections are updated with responses and marked with version increment
5. **Given** user running clarify after initial decompose, **When** ambiguities resolved, **Then** system prompts to re-run `/bp.decompose` to regenerate constitutions

---

### User Story 2 - Validate Constitution Consistency (Priority: P1)

After running `/bp.decompose`, a founder wants to verify that all generated constitutions (4 strategic + 5-10 feature) are consistent with each other and trace back correctly to the pitch deck.

**Why this priority**: Inconsistent constitutions lead to conflicting feature requirements. This catches errors before implementation, preventing wasted development effort. Essential for maintaining bidirectional traceability.

**Independent Test**: Run `/bp.analyze` after decomposition. System checks all constitution links, identifies orphaned principles, detects conflicts between strategic constitutions, and reports coverage gaps. Can be tested by intentionally breaking links or adding contradictory principles.

**Acceptance Scenarios**:

1. **Given** decomposed constitutions, **When** user runs `/bp.analyze`, **Then** system reports "All 4 strategic constitutions linked to pitch deck, all 7 feature constitutions linked to strategic principles, no conflicts detected"
2. **Given** a feature constitution with broken link to company-constitution.md#principle-5, **When** user runs `/bp.analyze`, **Then** system reports "ERROR: features/003-search.md references company#principle-5 which does not exist"
3. **Given** product constitution saying "Mobile-first" but market constitution saying "Desktop enterprise users", **When** user runs `/bp.analyze`, **Then** system flags "CONFLICT: product-constitution.md#principle-2 contradicts market-constitution.md#principle-1"
4. **Given** pitch deck section #go-to-market has no linked constitutions, **When** user runs `/bp.analyze`, **Then** system warns "COVERAGE GAP: pitch-deck.md#go-to-market not referenced by any strategic constitution"
5. **Given** analyze report with 2 errors and 1 warning, **When** user fixes issues and re-runs `/bp.analyze`, **Then** system confirms "All issues resolved - constitutions ready for implementation"

---

### User Story 3 - Generate Constitution Quality Checklists (Priority: P2)

A founder wants to ensure their constitutions meet quality standards before using them to build features with AI agents. They need a structured checklist to validate completeness, clarity, and actionability.

**Why this priority**: Quality gates prevent weak constitutions from reaching implementation. Lower priority than P1 items because manual review can catch many issues, but structured checklists improve consistency and thoroughness.

**Independent Test**: Run `/bp.checklist` after decomposition. System generates markdown checklists for strategic constitutions (4 checklists) and feature constitutions (5-10 checklists) in `.specify/checklists/`. User can review and check off items. Can be tested by validating checklist structure and completeness.

**Acceptance Scenarios**:

1. **Given** decomposed constitutions, **When** user runs `/bp.checklist`, **Then** system creates `.specify/checklists/company-constitution.md` with 10 validation items
2. **Given** strategic constitution checklist generated, **When** user opens it, **Then** checklist includes items like "□ All principles have measurable outcomes", "□ Each principle links back to pitch deck section", "□ No implementation details in principles"
3. **Given** feature constitution checklist generated, **When** user opens it, **Then** checklist includes items like "□ All user stories have acceptance criteria", "□ Success criteria are measurable and technology-agnostic", "□ Feature links to at least 1 strategic principle"
4. **Given** user has manually checked 8/10 items on company-constitution checklist, **When** they run `/bp.checklist --report`, **Then** system shows "Company Constitution: 80% complete (2 items remaining)"
5. **Given** all checklists 100% checked, **When** user runs `/bp.checklist --report`, **Then** system confirms "All constitutions passed quality review - ready for `/speckit.implement`"

---

### Edge Cases

- What happens when user runs `/bp.clarify` on a pitch deck that has already been decomposed? Should it warn about potential constitution regeneration?
- How does `/bp.analyze` handle circular references between constitutions (e.g., feature A depends on feature B which depends on feature A)?
- What if `/bp.checklist` is run before `/bp.decompose`? Should it generate template checklists or error?
- How does system handle version mismatches (e.g., pitch deck v2.0.0 but constitutions still reference v1.0.0)?
- What if user manually edits a constitution after decomposition - does `/bp.analyze` detect manual changes and flag them?

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide `/bp.clarify` command that analyzes pitch deck sections for ambiguities
- **FR-002**: `/bp.clarify` MUST identify missing required sections (company purpose, problem, solution, market size, competition, business model)
- **FR-003**: `/bp.clarify` MUST ask maximum 5 targeted questions to resolve critical ambiguities, prioritized by impact (scope > financials > strategy > details)
- **FR-004**: `/bp.clarify` MUST support `--section=<section-id>` flag to focus on specific pitch deck sections
- **FR-005**: `/bp.clarify` MUST update pitch deck in-place with clarification answers and increment version (PATCH bump)
- **FR-006**: System MUST provide `/bp.analyze` command that validates constitution consistency
- **FR-007**: `/bp.analyze` MUST check all traceability links (constitutions → pitch deck, features → strategic constitutions)
- **FR-008**: `/bp.analyze` MUST detect broken references and report file path + line number
- **FR-009**: `/bp.analyze` MUST identify conflicting principles across strategic constitutions (e.g., contradictory market positioning)
- **FR-010**: `/bp.analyze` MUST report coverage gaps (pitch deck sections not referenced by any constitution)
- **FR-011**: `/bp.analyze` MUST validate version consistency (all constitutions reference same pitch deck version)
- **FR-012**: System MUST provide `/bp.checklist` command that generates quality checklists for all constitutions
- **FR-013**: `/bp.checklist` MUST create checklist files in `.specify/checklists/` directory (one per constitution)
- **FR-014**: `/bp.checklist` MUST include constitution-type-specific validation items (strategic vs. feature)
- **FR-015**: `/bp.checklist` MUST support `--report` flag to show checklist completion status across all constitutions
- **FR-016**: Checklist items MUST be markdown checkboxes that users can manually check off
- **FR-017**: All three commands MUST be implemented as Claude Code slash commands (`.claude/commands/bp.*.md`)
- **FR-018**: Commands MUST work with existing `.specify/` directory structure from `/bp.decompose`
- **FR-019**: Commands MUST preserve existing pitch deck and constitution files (non-destructive unless updating based on user input)
- **FR-020**: System MUST log command execution results to `.specify/changelog/` with timestamp and summary

### Key Entities

- **Clarification Question**: Represents an ambiguity in pitch deck, includes question text, section reference, priority level, suggested answers
- **Analysis Report**: Contains lists of broken links, conflicts, coverage gaps, version mismatches, organized by severity (error/warning/info)
- **Checklist Item**: Individual validation criterion with checkbox status, description, rationale, and reference to constitution section
- **Checklist File**: Collection of checklist items for a specific constitution, includes completion percentage and last updated timestamp
- **Traceability Link**: Reference from constitution to pitch deck section or from feature to strategic constitution, includes source file, line number, target section ID

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can run `/bp.clarify` and receive actionable questions in under 10 seconds for a typical pitch deck
- **SC-002**: `/bp.analyze` detects 100% of broken traceability links when tested against intentionally corrupted constitutions
- **SC-003**: `/bp.checklist` generates complete checklists (10+ items per strategic constitution, 15+ items per feature constitution) in under 5 seconds
- **SC-004**: Users report that `/bp.clarify` reduces time spent on pitch deck revisions by at least 30% (measured via user surveys)
- **SC-005**: `/bp.analyze` catches at least 90% of constitution quality issues before they reach implementation (based on post-implementation defect analysis)
- **SC-006**: Teams using all 3 quality commands report 50% fewer constitutional amendments after initial MVP launch (compared to teams not using quality commands)
- **SC-007**: 80% of users who run `/bp.checklist` achieve 100% checklist completion before proceeding to implementation

## Assumptions

- Users have already installed BP-Kit and run `bpkit init`
- Users have created a pitch deck at `.specify/deck/pitch-deck.md` following Sequoia template
- For `/bp.analyze` and `/bp.checklist`, users have already run `/bp.decompose` to generate constitutions
- Users are comfortable editing markdown files manually (for updating pitch deck after clarifications and checking off checklist items)
- Claude Code is the primary runtime environment (slash commands are `.md` files in `.claude/commands/`)
- Users understand semantic versioning for tracking pitch deck and constitution versions
- Checklists are manually checked by users - no automated checking system (future enhancement)
- Standard markdown link format is used for traceability: `[text](../path/file.md#section-id)`

## Dependencies

- **Depends on**: BP-Kit Init (Feature 001) - requires `.specify/` directory structure
- **Depends on**: `/bp.decompose` command (assumed to exist) - required before `/bp.analyze` or `/bp.checklist` can run
- **Optional integration**: `.specify/changelog/` directory for logging command execution
- **Future dependency**: `/bp.sync` command (for propagating clarifications from pitch deck to constitutions)

## Out of Scope

- Automated checking of checklist items (manual process for MVP)
- Real-time collaboration features (multiple users editing same pitch deck)
- Visual diff viewer for comparing pitch deck versions (can use standard git diff)
- AI-powered conflict resolution between constitutions (system only detects conflicts, user resolves manually)
- Integration with external tools (Notion, Confluence, etc.) for pitch deck import
- Metrics dashboard showing quality trends over time (future enhancement)
- Automated testing of generated constitutions against success criteria

## Notes

### Design Philosophy

These commands mirror Speckit's quality workflow pattern:
- `/speckit.clarify` → `/bp.clarify` (pre-planning clarification)
- `/speckit.analyze` → `/bp.analyze` (post-generation validation)
- `/speckit.checklist` → `/bp.checklist` (quality gates)

The BP-Kit quality commands operate at the constitutional layer (business strategy) while Speckit quality commands operate at the feature implementation layer (technical execution).

### Workflow Integration

**Recommended BP-Kit workflow with quality commands**:

1. Create pitch deck → **Run `/bp.clarify`** → Resolve ambiguities
2. **Run `/bp.decompose`** → Generate constitutions
3. **Run `/bp.analyze`** → Validate consistency
4. Fix any errors/warnings from analyze report
5. **Run `/bp.checklist`** → Generate quality gates
6. Review and check off all checklist items
7. Proceed to implementation with `/speckit.implement` on each feature constitution

### Version Compatibility

All commands must handle multiple pitch deck and constitution versions gracefully:
- v1.0.0 (initial version after decompose)
- v1.1.0 (minor amendments after clarify)
- v2.0.0 (major strategic pivots)

Commands should warn if constitution versions are misaligned with pitch deck version.
