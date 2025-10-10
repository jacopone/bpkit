# [CONSTITUTION_TYPE] Constitution: [COMPANY_NAME]
<!-- Types: Company / Product / Market / Business -->

**Version**: 1.0.0
**Ratified**: [YYYY-MM-DD]
**Last Amended**: [YYYY-MM-DD]
**Status**: Active

---

## 🔗 Traceability Links

**Source Deck Sections**:
- Primary: [`pitch-deck.md#[SECTION_ID]`](../deck/pitch-deck.md#[SECTION_ID])
- Secondary: [`pitch-deck.md#[SECTION_ID_2]`](../deck/pitch-deck.md#[SECTION_ID_2])

**Derived From Deck Version**: [X.Y.Z]

**Downstream Impact** (What depends on this):
- Feature constitutions: `[FEATURE_IDS]` (e.g., 001, 002, 003)
- Other constitutions: `[CONSTITUTION_NAMES]`

**Change Protocol**:
- Amendments to this constitution MUST trigger review of:
  - Pitch deck section(s) listed above
  - All downstream feature constitutions
- Use `/bp.sync --check` to validate consistency

---

## Purpose

[Single sentence describing what this constitution governs]

**Scope**: [What decisions this constitution guides]

**Out of Scope**: [What this constitution does NOT govern]

---

## Core Principles

### <a id="principle-1"></a>Principle 1: [PRINCIPLE_NAME]

**Rule**: [What MUST or MUST NOT happen]

**Rationale**: [Why this principle exists - reference to pitch deck problem/solution]

**Source**: [`pitch-deck.md#[SECTION]`](../deck/pitch-deck.md#[SECTION]) - [Brief quote or reference]

**Test**: [How to verify compliance with this principle]

**Examples**:
- ✅ **Compliant**: [Example of following the principle]
- ❌ **Violation**: [Example of breaking the principle]

**Impact If Violated**: [Consequences of breaking this rule]

---

### <a id="principle-2"></a>Principle 2: [PRINCIPLE_NAME]

**Rule**: [What MUST or MUST NOT happen]

**Rationale**: [Why this principle exists]

**Source**: [`pitch-deck.md#[SECTION]`](../deck/pitch-deck.md#[SECTION]) - [Brief quote or reference]

**Test**: [How to verify compliance]

**Examples**:
- ✅ **Compliant**: [Example]
- ❌ **Violation**: [Example]

**Impact If Violated**: [Consequences]

---

[Add more principles as needed]

---

## Governance

### Amendment Process

**Trigger**: When to consider amending this constitution:
- [Condition 1]: [e.g., "Market positioning fundamentally shifts"]
- [Condition 2]: [e.g., "User feedback contradicts a principle"]
- [Condition 3]: [e.g., "New competitor invalidates differentiation"]

**Approval Required**:
- [Approval authority]: [e.g., "Founders", "Board", "Product team + CEO"]

**Impact Analysis Required**:
1. Run `/bp.sync --check` to identify affected artifacts
2. Review all downstream feature constitutions
3. Update pitch deck sections (with version bump)
4. Document rationale in `.specify/changelog/`

### Review Cycle

**Frequency**: [Monthly/Quarterly/Annually/As-needed]

**Review Criteria**:
- Are principles still aligned with market reality?
- Do metrics validate or contradict principles?
- Have competitive dynamics changed?

### Version Control

**Version Scheme**: MAJOR.MINOR.PATCH
- **MAJOR**: Principle removed or redefined (breaking change)
- **MINOR**: New principle added or existing principle expanded
- **PATCH**: Clarification, wording improvement, non-semantic change

**Current Version**: [X.Y.Z]

---

## Feedback Loop: Constitution ↔ Pitch Deck

### When This Constitution Changes

**Forward Propagation** (Constitution → Pitch Deck):
1. Constitution principle updated based on product learnings
2. Run `/bp.sync --reverse` to regenerate pitch deck
3. Deck sections [`#[SECTION_IDS]`](../deck/pitch-deck.md) auto-updated
4. Review diff before committing new deck version

**Example**: If `Principle 1` changes from "X" to "Y":
- Pitch deck `#[SECTION]` updates to reflect new strategy
- Changelog entry created: `.specify/changelog/YYYY-MM-DD-[topic].md`
- Deck version bumps: v1.0.0 → v1.1.0 (minor)

### When Pitch Deck Changes

**Backward Propagation** (Pitch Deck → Constitution):
1. Pitch deck updated for new investor presentation
2. Run `/bp.sync --forward` to update constitutions
3. This constitution's principles reviewed against new deck content
4. If conflict detected, `/bp.sync` prompts for resolution

**Example**: If pitch deck `#competition` section changes:
- Market constitution reviewed (if that's the source)
- Principles updated to match new competitive strategy
- Downstream features flagged for review

---

## Metrics & Validation

**Success Criteria** (How we know principles are working):
- **SC-[ID]-001**: [Measurable metric tied to Principle 1]
- **SC-[ID]-002**: [Measurable metric tied to Principle 2]

**Warning Signs** (Principle may need revision):
- ⚠️ [Metric or signal that indicates principle is wrong]
- ⚠️ [Metric or signal that indicates principle is wrong]

**Data Sources**:
- [Where to find validation data]: [e.g., "Analytics dashboard", "User interviews"]

---

## Appendix: Change History

**v1.0.0** (YYYY-MM-DD): Initial version derived from pitch deck v1.0.0
- Principles extracted from deck sections: [LIST]
- Ratified by: [WHO]

**v1.1.0** (YYYY-MM-DD): [Description of changes]
- Amended: Principle X
- Reason: [Why]
- Impacted: [What downstream artifacts updated]

---

## Document Metadata

**Template Version**: 1.0.0
**Constitution Type**: [Company/Product/Market/Business]
**Maintenance**: Generated by `/bp.decompose`, maintained by `/bp.sync`
**Related Documents**:
- Pitch Deck: [`../deck/pitch-deck.md`](../deck/pitch-deck.md)
- Feature Constitutions: [`../features/`](../features/)
- Changelog: [`../changelog/`](../changelog/)
