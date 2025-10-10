# BP-to-Constitution

**Transform business plans into executable MVP specifications for AI agents**

Based on Sequoia Capital's pitch deck template, this system decomposes business ideas into constitutional principles that AI coding agents can implement.

---

## The Closed Loop

```
┌──────────────────────────────────────────────────────────┐
│  1. Business Plan (Sequoia Pitch Deck)                   │
│     - Company purpose, problem, solution                  │
│     - Market, competition, business model                │
│     - Team, financials, vision                            │
└──────────────────────────────────────────────────────────┘
                        ↓ /bp.decompose
┌──────────────────────────────────────────────────────────┐
│  2. Strategic Constitutions (4 files)                    │
│     - Company: Mission, values, culture                   │
│     - Product: UX principles, feature priorities          │
│     - Market: Positioning, differentiation               │
│     - Business: Revenue model, unit economics             │
└──────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────┐
│  3. Feature Constitutions (5-10 files)                   │
│     - User management, listings, search, booking, etc.    │
│     - Each feature: User stories, entities, principles    │
│     - Linked to strategic constitutions + pitch deck      │
└──────────────────────────────────────────────────────────┘
                        ↓ /speckit.implement
┌──────────────────────────────────────────────────────────┐
│  4. AI Agents Build MVP                                  │
│     - Agents read feature constitutions                   │
│     - Generate plans, tasks, code                         │
│     - Measure success criteria                            │
└──────────────────────────────────────────────────────────┘
                        ↓ Metrics + Learnings
┌──────────────────────────────────────────────────────────┐
│  5. Feedback Loop (Constitutions Update)                 │
│     - Product iterations reveal insights                  │
│     - Constitutional principles evolve                    │
│     - Changelog documents changes                         │
└──────────────────────────────────────────────────────────┘
                        ↓ /bp.sync --to-deck
┌──────────────────────────────────────────────────────────┐
│  6. Updated Pitch Deck for Investors                     │
│     - Regenerated from constitutions                      │
│     - Includes traction data                              │
│     - Reflects pivots and learnings                       │
│     - Ready for next funding round                        │
└──────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Step 1: Decompose Your Business Plan

**Option A: Interactive** (recommended for first time)
```bash
/bp.decompose --interactive
```

**Option B: From existing markdown**
```bash
/bp.decompose --from-file my-pitch.md
```

**Option C: From PDF**
```bash
/bp.decompose --from-pdf pitch-deck.pdf
```

This creates:
- `.specify/deck/pitch-deck.md` (canonical source)
- `.specify/memory/` (4 strategic constitutions)
- `.specify/features/` (5-10 feature constitutions)

---

### Step 2: Review & Adjust

**Check consistency**:
```bash
/bp.sync --check
```

**Adjust feature priorities** (if needed):
```bash
/bp.adjust-priority 003 P1  # Promote feature to MVP critical
```

---

### Step 3: Implement MVP

**For each P1 feature** (in dependency order):

```bash
# Example: Implementing feature 001-user-management
/speckit.plan --constitution features/001-user-management.md
/speckit.tasks --constitution features/001-user-management.md
/speckit.implement --constitution features/001-user-management.md
```

Give these constitutions to AI agents (Claude Code, Cursor, etc.) and they'll build the features.

---

### Step 4: Iterate & Sync

**As you learn from users**:

1. **Update constitutions** based on product feedback
2. **Document changes** in `.specify/changelog/`
3. **Regenerate pitch deck** with new insights:

```bash
/bp.sync --to-deck
```

4. **Present updated deck** to investors with real traction data

---

## Directory Structure

```
.
├── .specify/
│   ├── deck/
│   │   └── pitch-deck.md               # Source of truth (Sequoia template)
│   ├── memory/
│   │   ├── company-constitution.md      # Mission, values, culture
│   │   ├── product-constitution.md      # UX principles, priorities
│   │   ├── market-constitution.md       # Positioning, competition
│   │   └── business-constitution.md     # Revenue, unit economics
│   ├── features/
│   │   ├── 001-user-management.md       # Feature constitution 1
│   │   ├── 002-listing-management.md    # Feature constitution 2
│   │   ├── 003-search-discovery.md      # Feature constitution 3
│   │   └── ...                          # More features (5-10 total for MVP)
│   ├── changelog/
│   │   └── YYYY-MM-DD-change-title.md   # Documents pivots/learnings
│   ├── templates/
│   │   ├── pitch-deck-template.md       # Sequoia template
│   │   ├── strategic-constitution-template.md
│   │   └── feature-constitution-template.md
│   └── FEATURE_MAP.md                   # Dependency graph + build order
├── .claude/
│   └── commands/
│       ├── bp.decompose.md              # Main decomposition command
│       └── bp.sync.md                   # Bidirectional sync command
└── README.md                            # This file
```

---

## Key Features

### 🔗 Bidirectional Traceability

Every constitutional principle links back to its source in the pitch deck:

```markdown
**Source**: [`pitch-deck.md#solution`](../deck/pitch-deck.md#solution)
```

Every feature links to strategic constitutions:

```markdown
**Upstream**: [`product-constitution.md#principle-1`](../memory/product-constitution.md#principle-1)
```

This enables:
- **Forward**: Pitch deck changes propagate to constitutions
- **Reverse**: Product learnings flow back to pitch deck
- **Validation**: Consistency checks across all levels

---

### 📊 Success Criteria

Feature constitutions include measurable success criteria:

```yaml
Success Criteria:
  - SC-002-001: "Users complete listing creation in <10 minutes"
  - SC-002-002: "95% of listings have ≥3 photos"
  - SC-002-003: "Photo upload success rate >99%"
```

These feed back into pitch deck's "Traction" section when you regenerate.

---

### 🤖 AI Agent Compatible

Feature constitutions are **complete specifications**:
- User stories (what to build)
- Data models (entities, relationships)
- Principles (constraints to enforce)
- Success criteria (how to validate)

Agents can take a feature constitution and run:
1. `/speckit.plan` → Generate technical plan
2. `/speckit.tasks` → Break into tasks
3. `/speckit.implement` → Build the feature

---

### 📝 Changelog-Driven Evolution

Every change documents:
- What changed (principle, feature, metric)
- Why (user feedback, metric data, competitive move)
- Impact (what downstream artifacts need updates)
- Next steps (action items)

This creates an audit trail from MVP to scale.

---

## Commands

### `/bp.decompose`

**Pitch deck → Constitutions**

Creates strategic + feature constitutions from business plan.

**Flags**:
- `--interactive`: Q&A mode (Sequoia template questions)
- `--from-file <path>`: Parse markdown file
- `--from-pdf <path>`: Extract from PDF
- `--dry-run`: Preview without writing files
- `--features <N>`: Target number of features (default: 5-10)

**Example**:
```bash
/bp.decompose --interactive --features 7
```

---

### `/bp.sync`

**Bidirectional sync between deck ↔ constitutions**

Maintains consistency as business evolves.

**Modes**:
- `--check`: Validate consistency (no changes)
- `--from deck`: Deck changed → Update constitutions
- `--to-deck`: Constitutions changed → Regenerate deck

**Flags**:
- `--interactive`: Review each change
- `--dry-run`: Preview changes
- `--verbose`: Show detailed analysis

**Examples**:
```bash
# Before investor meeting
/bp.sync --check

# After strategic pivot (deck updated)
/bp.sync --from deck --interactive

# After 6 months of product iteration
/bp.sync --to-deck --dry-run
```

---

### `/bp.validate`

**Deep consistency validation**

Checks for:
- Broken links
- Version mismatches
- Principle conflicts
- Missing success criteria
- Incomplete coverage

---

### `/bp.adjust-priority`

**Change feature priority**

```bash
/bp.adjust-priority <feature-id> <P1|P2|P3>

# Example: Demote feature 006 to post-MVP
/bp.adjust-priority 006 P2
```

---

## Example: AirBnB Use Case

**Input**: AirBnB pitch deck (Sequoia format)

**Output**:

**Strategic Constitutions**:
1. **Company**: Mission = "Democratize hospitality"
2. **Product**: Principle = "Local authenticity over generic hotels"
3. **Market**: Positioning = "Target budget-conscious travelers"
4. **Business**: Revenue = "10% commission on bookings"

**Feature Constitutions** (MVP):
1. User Management (Host/Guest roles)
2. Listing Management (Create/edit spaces)
3. Search & Discovery (Find by location/dates)
4. Booking System (Request, approve, confirm)
5. Payment Processing (Collect, commission, payout)

**Implementation**:
- Give 5 feature constitutions to AI agents
- Agents build MVP in dependency order
- Each feature validates against strategic principles

**Iteration**:
- After 6 months: 45% conversion vs. 60% projected
- Update product constitution: "Simplify booking flow"
- Run `/bp.sync --to-deck`
- New pitch deck shows traction + learnings

---

## Integration with Speckit

This system **extends Speckit** with business plan decomposition:

```
Speckit Workflow:
  /speckit.specify → spec.md
  /speckit.plan → plan.md
  /speckit.tasks → tasks.md
  /speckit.implement → code

BP-to-Constitution Workflow:
  /bp.decompose → feature constitutions (input to Speckit)
  [Use Speckit commands on each feature]
  /bp.sync --to-deck → updated pitch deck
```

**Feature constitutions** are **Speckit-compatible inputs** — they contain all information needed for `/speckit.plan` to generate implementation plans.

---

## Philosophy

### From Vision to Validated Product

Traditional approach:
1. Write pitch deck
2. ??? (gap)
3. Build product

**Problem**: No systematic translation from vision to implementation.

**This system**:
1. Write pitch deck (vision)
2. **Decompose into constitutions** (principles)
3. **Generate feature specs** (executable)
4. **AI agents implement** (code)
5. **Measure & learn** (reality)
6. **Update constitutions** (evolve)
7. **Regenerate deck** (revised vision)

The gap is filled with **constitutional principles** that preserve strategic intent while enabling tactical execution.

---

### Bidirectional Accountability

- **Downward**: Strategic decisions constrain features
- **Upward**: Product learnings refine strategy

Example:
- **Down**: Market constitution says "Target SMBs" → Features optimize for small business use cases
- **Up**: Features reveal "SMBs want mobile-first" → Market constitution updated, deck reflects this insight

---

### Executable Specifications

Feature constitutions are **complete enough for AI agents to build**, including:
- What (user stories)
- Why (rationale linked to pitch deck)
- How (entities, constraints)
- Success (measurable criteria)

No ambiguity. No "figure it out." Just build.

---

## Use Cases

### 1. Solo Founder → MVP

**You have**: Business idea in your head
**You want**: AI agents to build MVP

**Workflow**:
1. `/bp.decompose --interactive` (30 min to answer Sequoia questions)
2. Review 5-10 feature constitutions (adjust priorities)
3. Give to AI agents → MVP built in days

---

### 2. Startup → Seed Round

**You have**: Working MVP, ready to raise
**You need**: Pitch deck with traction

**Workflow**:
1. MVP metrics collected (conversion rates, growth, etc.)
2. Update feature constitutions with learnings
3. `/bp.sync --to-deck` → Generates pitch deck with real data
4. Present to investors

---

### 3. Product Pivot

**You have**: MVP, but market feedback says pivot needed
**You need**: Updated strategy + implementation plan

**Workflow**:
1. Update pitch deck with new strategy (target market, positioning, etc.)
2. `/bp.sync --from deck` → Constitutions update
3. Review affected features (some obsolete, some new)
4. Agents rebuild with new direction

---

### 4. Series A → Scale

**You have**: Traction, raising for growth
**You need**: Clear strategic principles for scaling team

**Workflow**:
1. Strategic constitutions = onboarding for new hires
2. Feature constitutions = product roadmap with rationale
3. Changelog = history of pivots and decisions
4. Pitch deck = always up-to-date for investors

---

## Technical Notes

### Sequoia Template Sections

1. **Company Purpose**: Single sentence mission
2. **Problem**: Customer pain points
3. **Solution**: Your unique approach
4. **Why Now**: Market timing
5. **Market Potential**: TAM/SAM/SOM, target customer
6. **Competition**: Landscape, differentiation
7. **Business Model**: Revenue model, unit economics
8. **Team**: Founders, key hires
9. **Financials**: Projections, use of funds
10. **Vision**: 5-year picture

### Constitution Types

**Strategic** (4 files, slow-changing):
- Company: Mission, values (immutable)
- Product: UX principles, priorities
- Market: Positioning, differentiation
- Business: Revenue model, economics

**Feature** (5-10 files, tactical):
- One per MVP feature
- User stories, entities, principles
- Linked to strategic constitutions
- Speckit-compatible

### Version Semantics

**Strategic Constitutions**:
- MAJOR: Principle removed/redefined (breaking)
- MINOR: Principle added
- PATCH: Clarification/wording

**Feature Constitutions**:
- MAJOR: Core entity/contract changed
- MINOR: User story added
- PATCH: Success criteria adjusted

**Pitch Deck**:
- MAJOR: Strategic pivot (market, model, positioning)
- MINOR: Section added (traction, updated financials)
- PATCH: Wording, typos, formatting

---

## Roadmap

**Current**: Manual decomposition + sync (AI-assisted)

**Future Enhancements**:
- Auto-extract from PDF with higher accuracy
- Template marketplace (SaaS, marketplace, mobile app archetypes)
- Metrics integration (auto-update from analytics dashboards)
- Multi-deck support (investor deck vs. team deck vs. customer deck)
- Compliance checking (feature violates constitutional principle → block merge)

---

## Contributing

This system is designed to be extended. Contribute by:

1. **Templates**: New constitution types (e.g., engineering-constitution.md for technical principles)
2. **Commands**: Additional workflows (e.g., `/bp.roadmap` for multi-quarter planning)
3. **Integrations**: Connect to project management tools (Linear, Jira) for automatic sync

---

## License

[Your license choice]

---

## Credits

- **Sequoia Capital**: Pitch deck template
- **Speckit**: Spec-driven development workflow
- **Claude Code**: AI agent implementation

---

## Questions?

**Q: How is this different from just using Speckit?**

A: Speckit helps with **feature development** (spec → plan → tasks → code). This system adds **business strategy decomposition** (pitch deck → constitutions → features). It bridges the gap from "why we exist" to "what to build."

**Q: Do I need to use Speckit?**

A: No. Feature constitutions are standalone specifications any AI agent can use. Speckit just provides a structured workflow.

**Q: What if my pitch deck changes?**

A: Run `/bp.sync --from deck` to propagate changes to constitutions, or `/bp.sync --to-deck` to regenerate the deck from evolved constitutions.

**Q: Can I have more than 10 features?**

A: Yes, but keep MVP tight (5-10 P1 features). Add more with `/bp.add-feature` as you grow.

**Q: What if I don't have a pitch deck yet?**

A: Start with `/bp.decompose --interactive`. It asks Sequoia template questions and builds your deck + constitutions simultaneously.

---

**Built for founders who want AI agents to build their MVP from a business plan.**
