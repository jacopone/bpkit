<!--
Sync Impact Report:
- Version: TEMPLATE → 1.0.0 (MINOR - Initial constitution)
- Added: All 5 core principles
- Added: Technology Constraints section
- Added: Speckit Integration section
- Templates requiring updates:
  ✅ plan-template.md (Constitution Check section to be verified)
  ✅ spec-template.md (No changes needed - business-agnostic)
  ✅ tasks-template.md (No changes needed - feature-agnostic)
- Follow-up TODOs: None
- Date: 2025-10-10
-->

# BP-Kit Constitution

## Core Principles

### I. Speckit Architecture Clone (NON-NEGOTIABLE)

BP-Kit MUST mirror Speckit's exact structure to ensure seamless integration and familiar developer experience.

**Requirements**:
- Python 3.11+ package using Typer + Rich for CLI (identical to Speckit)
- Installable via `uv tool install bpkit-cli --from git+https://github.com/user/bp-kit.git`
- Command-based workflow: `bpkit init`, `bpkit decompose`, `bpkit sync`
- Templates stored in `.specify/` directory alongside Speckit templates
- Slash commands in `.claude/commands/` for AI agent integration

**Rationale**: BP-Kit is a companion tool, not a replacement. Users who adopt Speckit expect consistent architecture, installation methods, and workflows. Diverging from Speckit's patterns would create cognitive overhead and reduce adoption.

**Test**: Install both Speckit and BP-Kit side-by-side. Verify no conflicts in:
- Directory structure (`.specify/` shared peacefully)
- Command namespaces (`specify` vs `bpkit`)
- Template naming conventions
- Python dependencies

**Violation Impact**: Breaking this principle means BP-Kit becomes standalone, requiring separate documentation, onboarding, and potentially conflicting with Speckit installations.

### II. Business-to-Code Bridge

Transform Sequoia-format pitch decks into two levels of executable constitutions that AI agents can implement.

**Decomposition Rules**:
- **Level 1 (Strategic)**: Generate exactly 4 constitutions from pitch deck sections:
  - `company-constitution.md` (from Company Purpose + Vision + Team)
  - `product-constitution.md` (from Problem + Solution + Why Now)
  - `market-constitution.md` (from Market Potential + Competition)
  - `business-constitution.md` (from Business Model + Financials + Team)

- **Level 2 (Feature)**: Generate 5-10 feature constitutions, each containing:
  - User stories (what to build)
  - Data models (entities, relationships, constraints)
  - Feature principles (derived from strategic constitutions)
  - Success criteria (measurable outcomes)
  - MVP boundaries (what's IN vs OUT of v1)

**Rationale**: Business plans articulate "why" and "what" at strategic level. AI agents need tactical "what" broken into features with enough detail to generate code. The two-level structure bridges this gap while maintaining traceability.

**Test**: Given AirBnB pitch deck, `bpkit decompose` MUST generate:
- 4 strategic constitutions (company, product, market, business)
- 5 feature constitutions minimum (user management, listing management, search, booking, payment)
- Each feature traceable to 1+ strategic constitutions
- Sum of features = viable MVP

**Violation Impact**: If decomposition logic is weak, generated constitutions will be too vague for agents to implement, requiring excessive human clarification.

### III. Bidirectional Traceability (NON-NEGOTIABLE)

Every constitutional principle MUST link to its source. Changes flow in both directions.

**Link Requirements**:
- **Strategic constitutions**: Every principle links to pitch deck section ID
  - Example: `**Source**: [`pitch-deck.md#solution`](../deck/pitch-deck.md#solution)`
- **Feature constitutions**: Every feature links to:
  - Strategic constitution principles that mandate it
  - Pitch deck sections that describe the user problem
  - Example: `**Upstream**: [`product-constitution.md#principle-1`](../memory/product-constitution.md#principle-1)`
- **Changelog entries**: Document every change with:
  - What changed (principle, feature, metric)
  - Why (trigger: deck update, product learning, pivot)
  - Impact (downstream artifacts requiring updates)
  - Links to all affected files

**Forward Flow** (Deck → Constitutions):
- User updates `pitch-deck.md` (e.g., changes business model)
- Runs `bpkit sync --from deck`
- Tool identifies changed sections, proposes constitution updates
- Shows impact: "Feature 005-payment needs review (business model changed)"

**Reverse Flow** (Constitutions → Deck):
- Product iteration reveals insights (e.g., "users prefer mobile-first")
- Developer updates `product-constitution.md` principle
- Creates changelog entry documenting the learning
- Runs `bpkit sync --to-deck`
- Tool regenerates pitch deck with updated Product section + Traction data

**Rationale**: Without traceability, constitutions become stale. Pitch deck promises don't reflect product reality. Investors see outdated decks. The feedback loop breaks.

**Test**:
- Change pitch deck `#business-model` section
- Run `bpkit sync --from deck`
- Verify `business-constitution.md` flagged for update
- Verify affected features (e.g., payment processing) listed in report

**Violation Impact**: Constitutions diverge from business strategy. Features built don't align with investor promises. No audit trail for pivots.

### IV. Speckit Compatibility

BP-Kit's output (feature constitutions) MUST be valid input to Speckit's workflow.

**Integration Requirements**:
- Feature constitutions are Speckit-compatible specifications
- Running `/speckit.plan --constitution features/001-user-management.md` MUST generate valid `plan.md`
- Running `/speckit.tasks --constitution features/001-user-management.md` MUST generate valid `tasks.md`
- Generated plans/tasks respect BP-Kit principles (traceability links, success criteria)

**Workflow**:
```bash
# BP-Kit generates feature constitutions
bpkit decompose --from-file pitch-deck.md

# Speckit consumes them
/speckit.plan --constitution features/001-user-management.md
/speckit.tasks --constitution features/001-user-management.md
/speckit.implement --constitution features/001-user-management.md
```

**Rationale**: BP-Kit solves "business plan → feature specs" problem. Speckit solves "feature specs → code" problem. They must compose. Feature constitutions bridge the gap.

**Test**:
- Generate feature constitution with `bpkit decompose`
- Pass to `/speckit.plan`
- Verify plan.md created without errors
- Verify plan includes Constitution Check section validating BP-Kit principles

**Violation Impact**: If feature constitutions aren't Speckit-compatible, users must manually rewrite them, defeating the purpose of automation.

### V. AI-Executable Specifications

Feature constitutions MUST be complete enough for AI agents to build MVPs without human clarification.

**Completeness Criteria**:
- **User Stories**: Prioritized (P1/P2/P3), independently testable, with acceptance criteria
- **Data Models**: Entities with attributes, relationships, constraints, lifecycle states
- **Principles**: Non-negotiable rules derived from strategic constitutions (e.g., "All listings require ≥1 photo")
- **Success Criteria**: Measurable outcomes (e.g., "95% photo upload success rate")
- **MVP Boundaries**: Explicit IN/OUT scope (e.g., "No multi-currency in v1")
- **Dependencies**: Clear prerequisite features and external services

**Quality Gates**:
- No `[NEEDS CLARIFICATION]` markers in generated constitutions (AI should make reasonable defaults)
- Every entity has ≥1 relationship to other entities (no orphans)
- Every user story maps to ≥1 entity or external service
- Every principle is testable (can write automated check)
- Success criteria include both quantitative (metrics) and qualitative (user satisfaction) measures

**Rationale**: Incomplete specs require back-and-forth clarification, slowing AI agents. The goal is "here's the constitution, build it" with zero human intervention for well-defined MVPs.

**Test**:
- Give feature constitution to AI agent (Claude, Cursor, Copilot)
- Agent should generate complete implementation without asking clarifying questions
- Verify generated code includes:
  - All entities from data model
  - Validation for all principles
  - Tests for success criteria

**Violation Impact**: Agents get stuck, ask questions, or make wrong assumptions. Developer spends time clarifying instead of reviewing generated code.

## Technology Constraints

BP-Kit MUST use these technologies to maintain Speckit compatibility:

- **Language**: Python 3.11+ (matches Speckit)
- **CLI Framework**: Typer (matches Speckit)
- **Console UI**: Rich (matches Speckit)
- **HTTP Client**: httpx[socks] (matches Speckit for template downloads)
- **Installation**: `uv tool install` (matches Speckit)
- **Package Structure**: `src/bpkit_cli/` with `__init__.py` defining `main()` entry point

**Template Format**:
- Markdown with YAML frontmatter (optional, for metadata)
- Stored in `.specify/deck/`, `.specify/memory/`, `.specify/features/`
- Use GitHub-flavored Markdown (fenced code blocks, tables, task lists)

**Slash Command Format**:
- Stored in `.claude/commands/bp.*.md`
- Contain execution instructions for AI agents
- Reference bash scripts in `.specify/scripts/bp/` for setup/validation tasks

## Speckit Integration

BP-Kit extends Speckit's workflow without replacing any part of it.

**Workflow Composition**:
```
Traditional Speckit:
1. /speckit.constitution → Define project principles
2. /speckit.specify → Write feature spec
3. /speckit.plan → Generate implementation plan
4. /speckit.tasks → Break into tasks
5. /speckit.implement → Build feature

BP-Kit + Speckit:
1. bpkit init → Add BP-Kit templates to Speckit project
2. bpkit decompose → Generate feature constitutions from pitch deck
3. /speckit.plan --constitution features/001-*.md → Use constitution as spec
4. /speckit.tasks --constitution features/001-*.md → Generate tasks
5. /speckit.implement → Build feature
6. bpkit sync --to-deck → Update pitch deck with traction
```

**Shared Directories**:
- `.specify/memory/`: Speckit's constitution + BP-Kit's strategic constitutions
- `.specify/features/`: BP-Kit's feature constitutions (consumed by Speckit)
- `.specify/templates/`: Both tools' templates coexist
- `.claude/commands/`: Both tools' slash commands coexist

**No Conflicts**:
- Speckit commands: `/speckit.*`
- BP-Kit commands: `/bp.*` or `bpkit` CLI
- Speckit focuses on single-feature development
- BP-Kit focuses on business-to-MVP decomposition

## Governance

**Constitution Supersedes**: All BP-Kit development decisions MUST align with these 5 principles. If a feature request conflicts with a principle, either reject the feature or propose constitutional amendment.

**Amendment Process**:
1. Propose change via GitHub issue or PR
2. Justify why principle is blocking legitimate use case
3. Community review (maintainers + 3 users minimum)
4. Version bump per semantic versioning:
   - MAJOR: Principle removed or redefined (breaking change)
   - MINOR: New principle added
   - PATCH: Clarification or wording improvement
5. Update templates (plan, spec, tasks) to reflect new principle
6. Update README and documentation

**Compliance Review**:
- Every PR MUST reference constitution principles it implements
- PRs violating principles are blocked until:
  - Code is revised to comply, OR
  - Constitutional amendment is proposed and approved
- Integration tests validate principle adherence (e.g., traceability links present)

**Version History**:
- v1.0.0 (2025-10-10): Initial constitution with 5 core principles

**Version**: 1.0.0 | **Ratified**: 2025-10-10 | **Last Amended**: 2025-10-10
