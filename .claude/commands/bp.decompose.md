---
description: "Decompose business plan (pitch deck) into strategic and feature constitutions for MVP development"
---

# Business Plan Decomposition Command

## Purpose

Transform a Sequoia-format pitch deck into:
1. **4 Strategic Constitutions** (Company, Product, Market, Business)
2. **5-10 Feature Constitutions** (MVP features that agents can implement)

All constitutions include bidirectional traceability links to enable the closed feedback loop.

---

## Usage

```bash
# Interactive mode: AI asks Sequoia template questions
/bp.decompose --interactive

# From markdown file
/bp.decompose --from-file .specify/deck/my-pitch.md

# From PDF
/bp.decompose --from-pdf ./pitch-deck.pdf

# Dry run (show what would be created without creating files)
/bp.decompose --interactive --dry-run
```

---

## Workflow

### Phase 1: Extract Business Plan Content

**Input Methods**:

1. **Interactive Q&A** (`--interactive`):
   - Ask user each Sequoia template question
   - Company Purpose → Problem → Solution → Why Now → etc.
   - Capture answers in structured format
   - Save to `.specify/deck/pitch-deck.md`

2. **From Markdown** (`--from-file`):
   - Read provided markdown file
   - Parse sections using headings/IDs
   - Validate all required sections present
   - If sections missing, switch to interactive mode for gaps

3. **From PDF** (`--from-pdf`):
   - Extract text from PDF
   - Use AI to map content to Sequoia sections
   - Prompt user for clarification on ambiguous sections
   - Save structured version to `.specify/deck/pitch-deck.md`

**Required Sections** (from Sequoia template):
- Company Purpose
- Problem
- Solution
- Why Now
- Market Potential
- Competition/Alternatives
- Business Model
- Team
- Financials (if available)
- Vision

---

### Phase 2: Generate Strategic Constitutions

**Output**: 4 files in `.specify/memory/`

#### 1. `company-constitution.md`

**Extracted From**:
- Deck `#company-purpose` → Mission (immutable)
- Deck `#vision` → 5-year vision
- Deck `#team` → Culture principles

**Principles Generated**:
- Mission statement (derived from Company Purpose)
- Core values (inferred from team story + vision)
- Long-term impact goals (from Vision section)

**Links Created**:
- `pitch-deck.md#company-purpose`
- `pitch-deck.md#vision`
- `pitch-deck.md#team`

---

#### 2. `product-constitution.md`

**Extracted From**:
- Deck `#problem` → User pain points
- Deck `#solution` → Product value proposition, "eureka moment"
- Deck `#why-now` → Product timing/enablers

**Principles Generated**:
- UX principles (derived from how solution addresses problem differently)
- Feature prioritization framework (what's core vs. nice-to-have)
- Product metrics (what defines product success)

**Example Principles**:
- "Every feature must solve [core problem] for [target user]"
- "UX simplicity over feature complexity"
- "Leverage [tech enabler from Why Now] in all features"

**Links Created**:
- `pitch-deck.md#problem`
- `pitch-deck.md#solution`
- `pitch-deck.md#why-now`

---

#### 3. `market-constitution.md`

**Extracted From**:
- Deck `#market` → Target customer, TAM/SAM/SOM
- Deck `#competition` → Competitive landscape, differentiation
- Deck `#why-now` → Market timing

**Principles Generated**:
- Target customer definition (who we serve, who we don't)
- Positioning strategy (how we compete, what we don't compete on)
- Market boundaries (scope limits)

**Example Principles**:
- "Target customer: [persona from market section]"
- "Differentiate on [X], not [Y]" (from competition section)
- "Geographic scope: [regions]" (from market size)

**Links Created**:
- `pitch-deck.md#market`
- `pitch-deck.md#competition`

---

#### 4. `business-constitution.md`

**Extracted From**:
- Deck `#business-model` → Revenue model, unit economics
- Deck `#financials` → Projections, use of funds
- Deck `#team` → Hiring principles, org structure

**Principles Generated**:
- Revenue model rules (how/when to monetize)
- Financial discipline (burn rate, profitability gates)
- Growth strategy (scaling levers)
- Team principles (hiring, structure)

**Example Principles**:
- "Revenue model: [X% commission on Y]" (from business model)
- "Unit economics: LTV:CAC > 3:1" (from financials)
- "Profitability target: [X months]" (from financial projections)

**Links Created**:
- `pitch-deck.md#business-model`
- `pitch-deck.md#financials`
- `pitch-deck.md#team`

---

### Phase 3: Identify MVP Features

**AI Analysis**: Based on pitch deck content, identify 5-10 core features needed for MVP.

**Methodology**:
1. **From Solution**: What are the key user actions described?
2. **From Problem**: What capabilities solve each pain point?
3. **From Business Model**: What features enable revenue?
4. **From Market**: What features serve the target customer?

**Feature Identification Template**:
- **Core Platform Features** (always needed):
  - User management (authentication, profiles, roles)
  - [Domain-specific core feature 1]
  - [Domain-specific core feature 2]
- **Transaction Features** (if marketplace/e-commerce):
  - Search/discovery
  - Booking/ordering
  - Payment processing
- **Communication Features**:
  - Messaging (if peer-to-peer)
  - Notifications
- **Trust Features**:
  - Reviews/ratings
  - Verification

**Priority Assignment** (P1/P2/P3):
- **P1 (MVP Critical)**: Features without which the solution doesn't work
- **P2 (Post-MVP)**: Features that enhance but aren't blocking
- **P3 (Growth)**: Features for scale, not validation

**Ask User for Confirmation**:
```
I've identified these MVP features:
1. [Feature 1] - P1 (MVP Critical)
2. [Feature 2] - P1 (MVP Critical)
3. [Feature 3] - P2 (Post-MVP)
4. [Feature 4] - P2 (Post-MVP)
5. [Feature 5] - P3 (Growth)

Do you want to:
- Proceed with these 5 features
- Add more features
- Change priorities
- Remove features
```

---

### Phase 4: Generate Feature Constitutions

**Output**: 5-10 files in `.specify/features/`

**For each feature**:

1. **Create Feature Constitution File**: `.specify/features/[###]-[feature-name].md`

2. **Extract Content**:
   - **Purpose**: From relevant pitch deck sections
   - **User Stories**: Derived from problem/solution
   - **Entities**: Inferred from feature requirements
   - **Principles**: Inherited from strategic constitutions

3. **Establish Links**:
   - **Upstream**: Link to pitch deck sections + strategic constitutions
   - **Dependencies**: Link to prerequisite features
   - **Downstream**: Note which features depend on this

4. **Define MVP Boundaries**:
   - What's IN scope for v1
   - What's OUT of scope (post-MVP)

**Example Feature Constitution Generation**:

```
Feature: Listing Management (for AirBnB-like product)

Sources:
- pitch-deck.md#solution: "Hosts can list their spare rooms"
- pitch-deck.md#business-model: "10% commission on bookings"
- product-constitution.md#principle-1: "Local authenticity over generic"

User Stories Generated:
- US1: Host creates listing (P1 - MVP)
- US2: Host edits listing (P1 - MVP)
- US3: Host manages calendar (P2 - Post-MVP)

Entities Generated:
- Listing (title, description, price, location, photos, status)
- Photo (url, caption, order)
- Calendar (available_dates, blocked_dates)

Principles Generated:
- FP1: "Listings must have ≥1 photo" (from product principle: transparency)
- FP2: "Accurate geocoding required" (from market principle: location-based)
```

---

### Phase 5: Validate & Link

**Consistency Checks**:

1. **Strategic Constitutions Align**:
   - Product principles don't contradict business model
   - Market positioning matches competitive strategy
   - Company mission consistent with product approach

2. **Feature Constitutions Complete**:
   - All P1 features together form viable MVP
   - Each feature maps to strategic principles
   - Dependencies are acyclic (no circular deps)

3. **Traceability Complete**:
   - Every principle links back to pitch deck section
   - Every feature links to strategic constitution
   - All links are bidirectional (can navigate both ways)

**Generate Dependency Graph**:
```
Features (dependency order):
1. 001-user-management (no deps)
2. 002-listing-management (depends on: 001)
3. 003-search-discovery (depends on: 002)
4. 004-booking-system (depends on: 001, 002, 003)
5. 005-payment-processing (depends on: 004)
```

**Ask User for Validation**:
```
Generated Artifacts:
✅ 4 strategic constitutions
✅ 5 feature constitutions
✅ All links validated
✅ Dependency graph created

Ready to write files. Proceed? [Y/n]
```

---

### Phase 6: Write Files

**Create All Files**:

1. `.specify/deck/pitch-deck.md` (if created from interactive/PDF)
2. `.specify/memory/company-constitution.md`
3. `.specify/memory/product-constitution.md`
4. `.specify/memory/market-constitution.md`
5. `.specify/memory/business-constitution.md`
6. `.specify/features/001-[feature].md` (x 5-10)
7. `.specify/FEATURE_MAP.md` (dependency graph + build order)

**Initialize Git Tracking**:
```bash
git add .specify/
git commit -m "feat: initial business plan decomposition

Generated from pitch deck v1.0.0:
- 4 strategic constitutions
- [N] feature constitutions
- Complete traceability links established

Next: Run /speckit.plan on each feature to generate implementation plans"
```

---

### Phase 7: Next Steps Guidance

**Output to User**:

```markdown
✅ Business Plan Decomposition Complete

**Created**:
- 4 Strategic Constitutions → `.specify/memory/`
- [N] Feature Constitutions → `.specify/features/`
- Pitch Deck Source → `.specify/deck/pitch-deck.md`

**MVP Features** (Priority order):
1. 001-[feature] (P1 - MVP Critical)
2. 002-[feature] (P1 - MVP Critical)
3. 003-[feature] (P1 - MVP Critical)
...

**Next Steps**:

1. **Review Constitutions**: Ensure principles match your vision
2. **Adjust Priorities**: Use `/bp.adjust-priority [feature-id] [P1/P2/P3]` if needed
3. **Start Implementation**:

```bash
# For each P1 feature (in dependency order):
/speckit.plan --constitution features/001-[feature].md
/speckit.tasks --constitution features/001-[feature].md
/speckit.implement --constitution features/001-[feature].md
```

4. **Track Progress**: Feature implementations feed back via `/bp.sync`
5. **Update Deck**: When ready for investors, run `/bp.sync --to-deck`

**Documentation**:
- Traceability: All links clickable in markdown viewers
- Dependency Graph: See `.specify/FEATURE_MAP.md`
- Change Protocol: See any constitution's "Governance" section
```

---

## Error Handling

**Missing Pitch Deck Sections**:
- If critical sections missing, prompt interactively for those sections only
- If user skips optional sections (e.g., Financials), note in constitutions as "TBD"

**Unclear Feature Identification**:
- If AI can't confidently identify features from pitch deck, ask user:
  ```
  I've identified [N] possible features. Which are MVP critical?
  [List features with checkboxes]
  ```

**Conflicting Principles**:
- If product principle conflicts with business model (e.g., "free forever" vs. "subscription revenue"):
  ```
  ⚠️ Conflict detected:
  - Product principle: [X]
  - Business principle: [Y]

  How should I resolve this?
  1. Adjust product principle
  2. Adjust business principle
  3. Accept conflict and document tradeoff
  ```

---

## Flags

- `--interactive`: Interactive Q&A mode
- `--from-file <path>`: Parse from markdown file
- `--from-pdf <path>`: Extract from PDF
- `--dry-run`: Show what would be created without writing files
- `--verbose`: Show detailed analysis during decomposition
- `--features <count>`: Target number of features (default: 5-10, AI decides)
- `--skip-strategic`: Only generate feature constitutions (assumes strategic exist)

---

## Examples

```bash
# Start from scratch with Q&A
/bp.decompose --interactive

# Use existing pitch deck markdown
/bp.decompose --from-file ./my-pitch.md

# Extract from PDF and review before writing
/bp.decompose --from-pdf ./pitch.pdf --dry-run

# Generate exactly 7 features
/bp.decompose --interactive --features 7
```

---

## Technical Implementation Notes

**For the agent executing this command**:

1. **Use structured prompting**: Walk through each phase sequentially
2. **Preserve user input**: Store raw answers in metadata for future reference
3. **Validate completeness**: Check all required sections before proceeding
4. **Smart linking**: Generate IDs consistently (e.g., `#company-purpose`, `#principle-1`)
5. **Template instantiation**: Use templates in `.specify/templates/`
6. **Version tracking**: Tag initial version as 1.0.0 for all constitutions
7. **Git integration**: Auto-commit on successful completion

---

## Related Commands

- `/bp.sync`: Bidirectional sync between constitutions and pitch deck
- `/bp.validate`: Check consistency across all constitutions
- `/bp.adjust-priority`: Change feature priority levels
- `/bp.add-feature`: Add new feature constitution after initial decomposition
