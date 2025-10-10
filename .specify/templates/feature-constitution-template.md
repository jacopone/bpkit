# Feature Constitution: [FEATURE_NAME]

**Feature ID**: [###]
**Version**: 1.0.0
**Status**: [Planning/In Development/Deployed/Deprecated]
**Priority**: [P1-MVP Critical / P2-Post MVP / P3-Growth]
**Estimated Complexity**: [Low/Medium/High]

---

## 🔗 Traceability Links

**Upstream Sources** (Why this feature exists):
- **Pitch Deck**:
  - [`pitch-deck.md#solution`](../deck/pitch-deck.md#solution) - [What problem this solves]
  - [`pitch-deck.md#market`](../deck/pitch-deck.md#market) - [What user need this addresses]
- **Strategic Constitutions**:
  - [`product-constitution.md#principle-[X]`](../memory/product-constitution.md#principle-[X]) - [Which principle mandates this]
  - [`business-constitution.md#[section]`](../memory/business-constitution.md#[section]) - [Business model connection]

**Dependencies** (What this feature needs):
- **Prerequisite Features**: [FEATURE_IDS] - [e.g., "001-user-management"]
- **External Systems**: [APIs, services, etc.]

**Dependents** (What depends on this):
- **Downstream Features**: [FEATURE_IDS] - [e.g., "004-booking-system needs listings"]
- **Business Metrics**: [Which KPIs this feature affects]

**Change Protocol**:
- Changes to this feature that alter core entities/contracts MUST update:
  - Dependent features: [LIST]
  - Strategic constitutions if pattern emerges
  - Pitch deck if results invalidate assumptions

---

## Feature Purpose

**One-Sentence Goal**: [What this feature accomplishes]

**User Problem Solved**: [Reference to pitch deck problem section]

**Business Value**: [Reference to business model section - how this drives revenue/growth]

---

## Alignment with Strategic Constitutions

Verify this feature aligns with all strategic principles:

- ✅ **Company Constitution**: [How it serves the mission]
- ✅ **Product Constitution**: [Which UX principles it upholds]
- ✅ **Market Constitution**: [Which customer segment it serves]
- ✅ **Business Constitution**: [How it supports revenue model]

**Conflicts/Tradeoffs**: [If this feature conflicts with any principle, justify why]

---

## User Stories (MVP Scope)

<!--
  Prioritized, independently testable user journeys.
  Each story maps to specific tasks in /speckit.tasks output.
-->

### <a id="us1"></a>US1 - [Story Title] (Priority: P1) 🎯 MVP

**As a** [user role]
**I want to** [capability]
**So that** [benefit/goal]

**Why This Priority**: [Explain why this is P1 - what value it delivers]

**Independent Test**: [How to verify this story works standalone]

**Acceptance Criteria**:
1. **Given** [context], **When** [action], **Then** [expected outcome]
2. **Given** [context], **When** [action], **Then** [expected outcome]
3. **Given** [context], **When** [action], **Then** [expected outcome]

**Metrics**:
- [Measurable success criterion]: [e.g., "Completion rate >80%"]

---

### <a id="us2"></a>US2 - [Story Title] (Priority: P2)

**As a** [user role]
**I want to** [capability]
**So that** [benefit/goal]

**Why This Priority**: [Explain priority level]

**Independent Test**: [How to verify standalone]

**Acceptance Criteria**:
1. **Given** [context], **When** [action], **Then** [expected outcome]
2. **Given** [context], **When** [action], **Then** [expected outcome]

---

[Add more user stories as needed]

---

## Core Entities (Data Model)

<!--
  Define entities this feature introduces or modifies.
  These become database tables, API models, etc.
-->

### <a id="entity-1"></a>[Entity1Name]

```yaml
Attributes:
  - id: UUID (primary key)
  - [attribute1]: [Type] (constraints, e.g., "String, max 100 chars, required")
  - [attribute2]: [Type] (constraints)
  - created_at: Timestamp
  - updated_at: Timestamp

Relationships:
  - belongs_to: [OtherEntity] (foreign key: [field])
  - has_many: [OtherEntity]
  - has_one: [OtherEntity]

Constraints:
  - [Business rule, e.g., "Price must be >$0"]
  - [Unique constraint, e.g., "Email unique per user"]

Indexes:
  - [Field(s) that need indexing for performance]

Lifecycle:
  - States: [enum values, e.g., "draft, published, archived"]
  - Transitions: [Valid state changes]
```

**Rationale**: [Why this entity exists - link to pitch deck problem/solution]

**Source**: Derived from [`pitch-deck.md#[section]`](../deck/pitch-deck.md#[section])

---

### <a id="entity-2"></a>[Entity2Name]

```yaml
Attributes:
  - [Define structure]

Relationships:
  - [Define relationships]
```

**Rationale**: [Why this entity exists]

---

## Feature Principles (Non-Negotiable)

<!--
  Rules specific to this feature that enforce strategic principles.
-->

### <a id="fp-1"></a>Feature Principle 1: [PRINCIPLE_NAME]

**Rule**: [What MUST or MUST NOT happen in this feature]

**Rationale**: [Why - reference to strategic constitution principle]

**Source**: [`[constitution].md#principle-[X]`](../memory/[constitution].md#principle-[X])

**Implementation**: [How to enforce this in code]

**Validation**: [How to test compliance]

**Example**:
- ✅ **Compliant**: [Code/behavior example]
- ❌ **Violation**: [Code/behavior example]

---

### <a id="fp-2"></a>Feature Principle 2: [PRINCIPLE_NAME]

**Rule**: [What MUST or MUST NOT happen]

**Rationale**: [Why]

**Source**: [`[constitution].md#[section]`](../memory/[constitution].md#[section])

**Implementation**: [How to enforce]

---

[Add more feature principles as needed]

---

## Technical Constraints

**Language/Framework**: [e.g., "Python 3.11 + FastAPI", "React 18 + Next.js"]

**Database**: [e.g., "PostgreSQL 15" - specify if spatial, full-text, or other features needed]

**External Services**: [APIs, SDKs, third-party integrations]

**Performance Requirements**:
- Response time: [e.g., "<200ms p95"]
- Throughput: [e.g., "1000 requests/second"]
- Data volume: [e.g., "Support 1M records"]

**Security/Compliance**: [Any specific requirements, e.g., "PCI compliance", "GDPR"]

**Platform**: [Web/Mobile/Desktop, OS versions, browser support]

---

## Success Criteria

<!--
  Measurable outcomes that define "done" and "successful".
  These feed back into pitch deck traction section.
-->

- **SC-[FID]-001**: [Measurable criterion, e.g., "Users complete flow in <2 minutes"]
- **SC-[FID]-002**: [Measurable criterion, e.g., "Error rate <1%"]
- **SC-[FID]-003**: [Measurable criterion, e.g., "80% user satisfaction score"]
- **SC-[FID]-004**: [Business metric, e.g., "10% increase in bookings"]

**Tracking**: [Where/how these metrics are measured]

**Threshold for Success**: [What metric values indicate this feature is working]

**Failure Triggers**: [What metrics would indicate this feature needs rework]

---

## MVP Boundaries

<!--
  Explicitly state what's IN and OUT of the initial version.
  Prevents scope creep, enables faster delivery.
-->

### ✅ IN Scope (MVP v1)

- [Feature/capability that MUST be in first version]
- [Feature/capability that MUST be in first version]
- [Feature/capability that MUST be in first version]

**Rationale**: [Why these are minimum viable]

### ❌ OUT of Scope (Post-MVP)

- [Feature/capability deferred to v2+]
- [Feature/capability deferred to v2+]
- [Feature/capability deferred to v2+]

**Rationale**: [Why these can wait - not critical for validation]

**Future Roadmap**: [When/why to revisit excluded features]

---

## Dependencies

### Prerequisite Features

**BLOCKS**: This feature cannot start until:
- [Feature ID]: [Feature name] - [What it provides that this needs]

### Concurrent Features

**INTEGRATES WITH**: Features that can be built in parallel but need coordination:
- [Feature ID]: [Feature name] - [What coordination is needed]

### Downstream Features

**ENABLES**: Features that depend on this being complete:
- [Feature ID]: [Feature name] - [What they consume from this feature]

---

## Implementation Guidance for AI Agents

<!--
  Concrete instructions for agents implementing this feature.
-->

### Build Order

1. **Data Models**: Create entities (tables/schemas) - [Reference #entity-1, #entity-2]
2. **User Story 1**: Implement end-to-end - [Reference #us1]
3. **User Story 2**: Add next priority - [Reference #us2]
4. **Validation**: Verify all feature principles - [Reference #fp-1, #fp-2]
5. **Success Criteria**: Measure and validate - [Reference success criteria section]

### Speckit Workflow

```bash
# Agent receives this constitution and runs:

# Step 1: Generate technical plan
/speckit.plan --constitution features/[###]-[feature-name].md

# Step 2: Generate executable tasks
/speckit.tasks --constitution features/[###]-[feature-name].md

# Step 3: Implement feature
/speckit.implement --constitution features/[###]-[feature-name].md

# Step 4: Validate against success criteria
/speckit.validate --metrics success-criteria
```

### Key Considerations

- **Principle Enforcement**: Validate [#fp-1, #fp-2] in unit tests
- **Dependencies**: Ensure [prerequisite features] are complete
- **Performance**: Profile against [technical constraints]
- **Error Handling**: [Specific error scenarios to handle]

---

## Feedback Loop Triggers

<!--
  When to update this constitution or upstream artifacts.
-->

### Update This Constitution If:

- ⚠️ [Success criterion] not met after 2 iterations → Feature principle may be wrong
- ⚠️ User feedback contradicts a feature principle
- ⚠️ Technical constraints prove infeasible
- ⚠️ MVP boundaries too narrow/too wide based on user testing

**Process**:
1. Document issue in `.specify/changelog/YYYY-MM-DD-[topic].md`
2. Update constitution with revised principle/scope
3. Run `/bp.sync --check` to identify upstream impacts

### Update Strategic Constitutions If:

- 📈 Pattern emerges across multiple features (e.g., all features struggle with same UX principle)
- 📈 Feature success invalidates a strategic assumption
- 📈 User segment behaves differently than market constitution assumed

**Process**:
1. Create changelog entry documenting pattern
2. Run `/bp.sync --reverse` to propose strategic constitution update
3. Review and approve upstream changes
4. Regenerate pitch deck if strategic shift is significant

### Update Pitch Deck If:

- 🎯 Feature delivers unexpected traction → Update "Traction" section
- 🎯 Feature validates/invalidates a key assumption → Update "Market" or "Solution"
- 🎯 Feature costs differ significantly from projections → Update "Financials"

**Process**:
1. Document learning in changelog
2. Run `/bp.sync --to-deck` to generate updated pitch deck
3. Review diff and approve changes
4. Version bump pitch deck appropriately

---

## Change History

**v1.0.0** (YYYY-MM-DD): Initial version
- Derived from pitch deck v[X.Y.Z]
- Strategic constitutions: [LIST]
- Created by: `/bp.decompose`

---

## Document Metadata

**Template Version**: 1.0.0
**Feature Type**: [Core/Enhancement/Integration]
**Speckit Compatible**: Yes
**Maintenance**: Generated by `/bp.decompose`, updated manually or via `/bp.sync`

**Related Documents**:
- Pitch Deck: [`../deck/pitch-deck.md`](../deck/pitch-deck.md)
- Strategic Constitutions: [`../memory/*-constitution.md`](../memory/)
- Speckit Spec: `../specs/[###]-[feature-name]/spec.md` (generated by `/speckit.specify`)
- Speckit Plan: `../specs/[###]-[feature-name]/plan.md` (generated by `/speckit.plan`)
- Speckit Tasks: `../specs/[###]-[feature-name]/tasks.md` (generated by `/speckit.tasks`)
