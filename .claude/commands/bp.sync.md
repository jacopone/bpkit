---
description: "Bidirectional sync between pitch deck and constitutions - the closed feedback loop"
---

# Business Plan Sync Command

## Purpose

Maintain consistency between pitch deck and constitutions in **both directions**:
- **Forward**: Pitch deck changes → Update constitutions
- **Reverse**: Constitution changes (from product learnings) → Regenerate pitch deck
- **Check**: Validate consistency without making changes

This creates the closed feedback loop: Vision → Features → Learnings → Updated Vision

---

## Usage

```bash
# Check for inconsistencies (no changes made)
/bp.sync --check

# Update constitutions from latest pitch deck
/bp.sync --from deck

# Regenerate pitch deck from constitutions + changelog
/bp.sync --to-deck

# Interactive mode: Review and approve each change
/bp.sync --to-deck --interactive

# Show what would change without applying
/bp.sync --to-deck --dry-run
```

---

## Workflow: Forward Sync (Deck → Constitutions)

**Trigger**: Pitch deck updated for new investor presentation, strategic pivot, etc.

### Phase 1: Detect Changes

**Compare**:
- Current pitch deck: `.specify/deck/pitch-deck.md`
- Deck version referenced in constitutions: `[source metadata]`

**Identify Modified Sections**:
```
Changes detected in pitch deck v1.0.0 → v2.0.0:
- #business-model: Pricing changed from subscription to transaction
- #competition: New competitor added
- #market: TAM updated based on new research
```

---

### Phase 2: Map to Affected Constitutions

**For each changed section**, identify impacted constitutions:

| Deck Section Changed | Constitution Affected | Principle Impacted |
|----------------------|----------------------|-------------------|
| `#company-purpose` | `company-constitution.md` | Mission statement |
| `#problem` | `product-constitution.md` | User pain points |
| `#solution` | `product-constitution.md` | UX principles |
| `#why-now` | `product-constitution.md` | Product timing |
| `#market` | `market-constitution.md` | Target customer |
| `#competition` | `market-constitution.md` | Positioning |
| `#business-model` | `business-constitution.md` | Revenue model |
| `#financials` | `business-constitution.md` | Unit economics |
| `#team` | `business-constitution.md` | Hiring principles |
| `#vision` | `company-constitution.md` | 5-year vision |

---

### Phase 3: Propose Constitution Updates

**For each affected constitution**:

1. **Show Diff**:
```diff
business-constitution.md#revenue-model

- Revenue Model: Monthly subscription ($99/month)
+ Revenue Model: Transaction fee (10% commission)

Rationale:
- OLD: Predictable recurring revenue
+ NEW: Lower barrier to entry, scales with usage

Source: pitch-deck.md#business-model v2.0.0
```

2. **Identify Downstream Impact**:
```
This change affects:
- Feature 005-payment-processing.md (implements revenue model)
  → Will need to update from subscription billing to transaction fees
- Success criteria: LTV calculation changes
```

3. **Ask User for Approval**:
```
Apply this change to business-constitution.md?
[Y]es / [N]o / [E]dit / [S]kip all
```

---

### Phase 4: Update Constitutions

**For approved changes**:

1. **Update Constitution File**:
   - Modify affected principle
   - Update version (MAJOR/MINOR/PATCH based on change type)
   - Update `Last Amended` date
   - Update `Source Deck Version` reference

2. **Create Changelog Entry**:
   - File: `.specify/changelog/YYYY-MM-DD-revenue-model-change.md`
   - Content:
     ```markdown
     # Revenue Model Change: Subscription → Transaction Fee

     **Date**: 2025-01-15
     **Trigger**: Pitch deck v2.0.0 update for Series A
     **Type**: Strategic Pivot

     ## What Changed

     **Constitution**: business-constitution.md
     **Section**: Revenue Model (Principle 1)
     **Version**: 1.0.0 → 2.0.0 (MAJOR)

     **Old**: Monthly subscription ($99/month)
     **New**: Transaction fee (10% commission)

     **Rationale**: Market feedback indicated pricing barrier for SMBs

     ## Downstream Impact

     **Feature Constitutions Affected**:
     - 005-payment-processing.md
       - Needs: Rewrite billing logic
       - Status: Flagged for update

     **Pitch Deck Sections Updated**:
     - #business-model (source of change)
     - #financials (LTV/CAC calculations updated)

     ## Next Steps

     - [ ] Review 005-payment-processing.md and update implementation
     - [ ] Recalculate unit economics with new model
     - [ ] Update financial projections
     ```

3. **Flag Affected Features**:
   - Add warning to feature constitution:
     ```markdown
     ⚠️ **ATTENTION**: Upstream change detected
     - business-constitution.md revenue model changed
     - This feature's implementation may need updates
     - See: .specify/changelog/2025-01-15-revenue-model-change.md
     ```

---

### Phase 5: Validation

**Check Consistency**:
- All constitutions reference correct deck version
- All changelog entries created
- No orphaned references
- Dependency graph still valid

**Report**:
```
✅ Forward Sync Complete

Updated:
- business-constitution.md (1.0.0 → 2.0.0)
- market-constitution.md (1.0.3 → 1.0.4)

Flagged for Review:
- Feature 005-payment-processing.md

Changelog Created:
- .specify/changelog/2025-01-15-revenue-model-change.md

Next: Review flagged features and update as needed
```

---

## Workflow: Reverse Sync (Constitutions → Deck)

**Trigger**: Product iterations reveal learnings that invalidate pitch deck assumptions.

### Phase 1: Collect Changes from Constitutions + Changelog

**Sources**:
1. **Constitution Version Changes**: Compare current vs. versions in deck metadata
2. **Changelog Entries**: Read all `.specify/changelog/*.md` since last deck update
3. **Feature Metrics**: Actual performance vs. projected (from success criteria)

**Example Inputs**:
```
Changelog Entries Since Last Deck Update:
1. 2025-01-15: Revenue model changed (subscription → transaction)
2. 2025-02-01: Target customer refined (all travelers → business travelers)
3. 2025-02-10: Competitive advantage updated (price → convenience)

Feature Metrics (Actual vs. Projected):
- Feature 002-listing-management:
  - Projected: Hosts create listing in <10 min
  - Actual: Average 6 min (overperforming)
- Feature 004-booking-system:
  - Projected: 60% conversion rate
  - Actual: 45% conversion rate (underperforming - UX issue identified)
```

---

### Phase 2: Map Changes to Deck Sections

**For each change**, determine which deck section needs update:

| Change Type | Source | Deck Section to Update |
|-------------|--------|----------------------|
| Revenue model change | `business-constitution.md` | `#business-model` |
| Target customer refined | `market-constitution.md` | `#market` |
| Competitive advantage | `market-constitution.md` | `#competition` |
| Metric overperformance | Feature success criteria | `#traction` (new section) |
| Metric underperformance | Feature success criteria | `#solution` (UX adjustment) |
| Strategic principle added | `product-constitution.md` | `#solution` or `#why-now` |

---

### Phase 3: Generate Updated Deck Sections

**For each affected section**:

1. **Read Current Section** from pitch deck
2. **Apply Constitutional Changes**:
   - Update text to reflect new principles
   - Add traction data if metrics available
   - Revise assumptions based on learnings
3. **Preserve Tone**: Maintain pitch deck narrative style (investor-focused)
4. **Add Evidence**: Link to metrics/data where available

**Example**:

**OLD `#business-model` Section**:
```markdown
## 7. Business Model

**Primary Revenue Stream**: Monthly subscription
- Pricing: $99/month for unlimited bookings
- Target: Power users who book frequently

**Unit Economics**:
- LTV: $1,200 (12-month avg retention)
- CAC: $300
- LTV:CAC: 4:1
```

**NEW `#business-model` Section** (after constitutional change):
```markdown
## 7. Business Model

**Primary Revenue Stream**: Transaction fees
- Pricing: 10% commission on each booking
- Rationale: Lower barrier to entry, aligns incentives with customer success

**Unit Economics** (Updated with actual data):
- LTV: $1,500 (based on 6-month actual data)
- CAC: $280 (improved through organic growth)
- LTV:CAC: 5.4:1 (exceeds 3:1 target)

**Validation**: After testing both models, transaction fees yield:
- 3x higher conversion rate (lower upfront cost)
- Better long-term retention (customers pay as they use)
- Data source: `.specify/changelog/2025-01-15-revenue-model-change.md`
```

**NEW `#traction` Section** (added based on metrics):
```markdown
## Appendix: Traction & Metrics (Updated 2025-02-15)

**Product Metrics** (Last 90 days):
- Listings created: 1,250
- Active hosts: 850 (68% activation rate)
- Bookings completed: 3,400
- Average booking value: $180
- Repeat booking rate: 35%

**Validation of Key Assumptions**:
- ✅ Assumption: Hosts can create listings quickly
  - Projected: <10 minutes | Actual: 6 minutes avg
- ⚠️ Assumption: 60% booking conversion rate
  - Projected: 60% | Actual: 45% (UX improvement in progress)

**Growth Trajectory**:
- MRR: $15,300 (from $0 6 months ago)
- Month-over-month growth: 40%
- Burn rate: $25k/month
- Runway: 18 months

**Customer Validation**:
- NPS Score: 62 (industry avg: 30-40)
- Host satisfaction: 4.7/5.0
- Guest satisfaction: 4.5/5.0

Source: Feature success criteria + analytics dashboard
```

---

### Phase 4: Version & Review

**Generate New Deck Version**:
1. **Copy Current Deck**: `pitch-deck.md` → `pitch-deck-v2.0.0.md`
2. **Apply Updates**: Modify affected sections
3. **Update Metadata**:
   ```markdown
   **Version**: 2.0.0 (was 1.0.0)
   **Date**: 2025-02-15
   **Status**: Ready for Series A
   ```
4. **Add Version History**:
   ```markdown
   ## Version History
   - v2.0.0 (2025-02-15): Updated with 6 months traction data
     - Business model changed to transaction fees
     - Target market refined to business travelers
     - Added traction section with real metrics
     - Source: Constitutional updates + changelog
   - v1.0.0 (2024-08-01): Initial deck for seed round
   ```

**Show Diff to User**:
```bash
git diff pitch-deck.md pitch-deck-v2.0.0.md

# Highlights:
# - Business model section: Subscription → Transaction
# - Traction section: ADDED (new)
# - Financials: Updated with actual metrics
# - Competition: Repositioned based on learnings
```

**Ask for Approval**:
```
Generated pitch deck v2.0.0 from constitutions + changelog.

Changes:
- Business model updated
- Traction section added with 6mo metrics
- Financials reflect actual unit economics
- Market positioning refined

Actions:
[A]pprove and replace pitch-deck.md
[S]ave as pitch-deck-v2.0.0.md (keep both versions)
[E]dit before saving
[C]ancel
```

---

### Phase 5: Update Constitution Metadata

**After deck regenerated**:

Update all constitutions' metadata:
```markdown
**Source Deck Version**: 2.0.0 (updated from 1.0.0)
**Last Synced**: 2025-02-15
```

This closes the loop: constitutions now reference the deck they helped generate.

---

## Workflow: Consistency Check

**Trigger**: Periodic validation (before investor meetings, quarterly reviews, etc.)

### Phase 1: Validate Links

**Check**:
1. **Every constitutional principle** links to a valid deck section
2. **Every feature constitution** links to valid strategic constitutions
3. **No broken references** (deck sections exist, IDs match)

**Report**:
```
🔗 Link Validation:
✅ All pitch deck section IDs valid
✅ All strategic constitution references valid
❌ Feature 006-messaging.md references deck#why-now (section renamed)
   → Suggested fix: Update link to deck#market-timing
```

---

### Phase 2: Version Consistency

**Check**:
1. All constitutions reference same deck version
2. Deck version matches what constitutions were generated from
3. No orphaned changes (deck updated but constitutions not synced)

**Report**:
```
📊 Version Consistency:
⚠️ Mismatch detected:
- Pitch deck: v2.0.0
- company-constitution.md references: v2.0.0 ✅
- product-constitution.md references: v1.0.0 ❌
- market-constitution.md references: v2.0.0 ✅
- business-constitution.md references: v2.0.0 ✅

Recommendation: Run `/bp.sync --from deck` to update product-constitution.md
```

---

### Phase 3: Principle Conflicts

**Check**:
1. **Cross-constitution conflicts**:
   - Product principle contradicts business model?
   - Market positioning conflicts with competitive strategy?
2. **Feature-to-strategic conflicts**:
   - Feature principles violate strategic principles?

**Example Conflict**:
```
⚠️ Potential Conflict:
- product-constitution.md#principle-2: "Always free for users"
- business-constitution.md#revenue-model: "Subscription fees from users"

This conflict may indicate:
1. Freemium model (free tier + paid upgrades) - document in both constitutions
2. Different revenue source (B2B not B2C) - clarify in market constitution
3. Outdated principle - one needs updating

Resolve this conflict? [Y/n]
```

---

### Phase 4: Completeness Check

**Verify**:
1. **All Sequoia sections covered**: Does pitch deck have all required sections?
2. **All MVP features identified**: Do feature constitutions sum to viable MVP?
3. **All principles testable**: Can each principle be validated with metrics?

**Report**:
```
✅ Completeness Check:
✅ Pitch deck has all 10 Sequoia sections
✅ MVP features cover core user journeys
⚠️ Missing success criteria:
   - product-constitution.md#principle-3 has no measurable test
   → Add: "Success criteria: [metric]"

Recommendation: Review and add success criteria where missing
```

---

## Error Handling

**Broken Links**:
```
❌ Error: Constitution references deck#old-section-name
Deck section renamed to #new-section-name

Fix: Update link in constitution? [Y/n]
```

**Version Mismatch**:
```
⚠️ Warning: Constitution generated from deck v1.0, current deck is v2.0

Options:
1. Sync constitutions to deck v2.0 (/bp.sync --from deck)
2. Regenerate deck from constitutions (/bp.sync --to-deck)
3. Ignore (manual review needed)
```

**Conflicting Changes**:
```
❌ Conflict: Both deck AND constitution changed same principle

Deck says: "Target market: All travelers"
Constitution says: "Target market: Business travelers"

Which is correct?
[D]eck wins (update constitution)
[C]onstitution wins (update deck)
[M]anual merge
```

---

## Changelog Template

**Auto-generated when changes detected**:

```markdown
# [Change Title]

**Date**: YYYY-MM-DD
**Trigger**: [What caused this change]
**Type**: [Strategic Pivot / Tactical Adjustment / Metric Update / Bug Fix]

## What Changed

**Constitution**: [constitution-name].md
**Section**: [Section/Principle ID]
**Version**: X.Y.Z → X.Y.Z (MAJOR/MINOR/PATCH)

**Old**: [Previous content]
**New**: [New content]

**Rationale**: [Why this change was made]

## Upstream Impact (Deck)

**Pitch Deck Sections Affected**:
- #[section-id]: [How it changed]

## Downstream Impact (Features)

**Feature Constitutions Affected**:
- [feature-id]: [What needs updating]

## Evidence/Data

**Supporting Metrics**:
- [Metric]: [Value] (source: [where])

**User Feedback**:
- [Quote or data point]

## Next Steps

- [ ] [Action item 1]
- [ ] [Action item 2]

## Related Changes

**See Also**:
- [Link to related changelog entries]
```

---

## Flags

- `--check`: Validate consistency without making changes
- `--from deck`: Update constitutions from pitch deck
- `--to-deck`: Regenerate pitch deck from constitutions
- `--interactive`: Review and approve each change
- `--dry-run`: Show what would change without applying
- `--verbose`: Show detailed analysis
- `--force`: Skip confirmations (use carefully)

---

## Examples

```bash
# Before investor meeting: ensure everything is consistent
/bp.sync --check

# Pitch deck updated for new round
/bp.sync --from deck --interactive

# Product learnings accumulated, regenerate deck
/bp.sync --to-deck --dry-run
/bp.sync --to-deck  # After reviewing dry run

# Quick consistency check
/bp.sync --check --verbose
```

---

## Integration with Speckit

**When features are implemented**:

1. **Feature completes**: `/speckit.implement` finishes
2. **Metrics collected**: Success criteria measured
3. **Constitution updated**: If metrics reveal principle issues
4. **Changelog created**: Document what changed and why
5. **Sync triggered**: `/bp.sync --to-deck` regenerates pitch with traction

**This creates the full loop**:
```
Pitch Deck (Vision)
    ↓
Constitutions (Principles)
    ↓
Features (Implementation via Speckit)
    ↓
Metrics (Reality Check)
    ↓
Constitutional Updates (Learnings)
    ↓
Updated Pitch Deck (Evolved Vision)
    ↓
[Repeat]
```

---

## Related Commands

- `/bp.decompose`: Initial generation from pitch deck
- `/bp.validate`: Deep validation with recommendations
- `/bp.add-feature`: Add new feature constitution mid-development
- `/bp.adjust-priority`: Reprioritize features based on learnings
