# Quickstart: BP-Kit Build - Pitch Deck Decomposition

**Feature**: 003-implement-bp-decompose
**Date**: 2025-10-11
**Audience**: Founders, product managers, AI agents

---

## What Is This?

The `/bp.decompose` command transforms Sequoia Capital pitch decks into executable constitutional specifications. It generates:
- **4 strategic constitutions** (company, product, market, business)
- **5-10 feature constitutions** (MVP capabilities)
- **Bidirectional traceability** (every principle links to business vision)

---

## Three Ways to Decompose

### Mode 1: Interactive (Start from Scratch)

**When to use**: You have a business idea but no pitch deck yet.

```bash
# Initialize BP-Kit project
bpkit init my-startup

# Run interactive decomposition
cd my-startup
bpkit decompose --interactive

# Answer 10 Sequoia section questions:
# 1. Company Purpose → "What is your mission?"
# 2. Problem → "What pain do customers feel?"
# 3. Solution → "How do you solve it?"
# ... (7 more sections)

# Result: pitch-deck.md + 4 strategic + 7 feature constitutions
```

**Time**: ~15 minutes
**Output**: Complete constitutional system from zero prior artifacts

---

### Mode 2: From Markdown File (Existing Pitch Deck)

**When to use**: You already have a pitch deck in markdown format (Obsidian, Notion, manual).

```bash
# Decompose existing markdown pitch deck
bpkit decompose --from-file ~/Documents/my-pitch.md

# System:
# - Parses 10 Sequoia sections (h2 headings)
# - Copies to .specify/deck/pitch-deck.md (canonical location)
# - Generates constitutions with traceability

# Result: 4 strategic + N feature constitutions
```

**Time**: <2 minutes
**Output**: Constitutions from existing markdown

---

### Mode 3: From PDF (Presentation Deck)

**When to use**: You have a PowerPoint/Keynote deck exported as PDF.

```bash
# Extract and decompose PDF pitch deck
bpkit decompose --from-pdf ~/Downloads/pitch-deck.pdf

# System:
# - Extracts text with PyMuPDF
# - Detects section boundaries (font size heuristics)
# - Generates markdown pitch deck
# - Creates constitutions

# Note: Check extraction quality, may need manual review
```

**Time**: <2 minutes (+ manual review if low confidence)
**Output**: Markdown pitch deck + constitutions

---

## What Gets Generated?

### Directory Structure After Decomposition

```
my-startup/
├── .specify/
│   ├── deck/
│   │   └── pitch-deck.md                    # ✅ 10 Sequoia sections
│   ├── memory/
│   │   ├── company-constitution.md          # ✅ Strategic (Company Purpose, Problem, Why Now)
│   │   ├── product-constitution.md          # ✅ Strategic (Solution, Product features)
│   │   ├── market-constitution.md           # ✅ Strategic (Market Size, Competition)
│   │   └── business-constitution.md         # ✅ Strategic (Business Model, Financials, Team)
│   ├── features/
│   │   ├── 001-user-management.md           # ✅ Feature (user stories, entities, criteria)
│   │   ├── 002-listing-management.md        # ✅ Feature
│   │   ├── 003-search-discovery.md          # ✅ Feature
│   │   ├── 004-booking-system.md            # ✅ Feature
│   │   ├── 005-payment-processing.md        # ✅ Feature
│   │   ├── 006-review-system.md             # ✅ Feature
│   │   └── 007-host-dashboard.md            # ✅ Feature (5-10 total)
│   └── changelog/
│       └── 2025-10-11-decompose-v1.0.0.md   # ✅ Audit trail
```

---

## Example: AirBnB Pitch Deck Decomposition

### Input Pitch Deck (Simplified)

**Section: Problem**
> Price is an important concern for customers booking travel online. Hotels leave you disconnected from the city and its culture. No easy way exists to book a room with a local or become a host.

**Section: Solution**
> SAVE MONEY when traveling. MAKE MONEY when hosting. SHARE CULTURE - local connection to the city.

**Section: Business Model**
> 10% commission on each transaction. Average booking: $70/night @ 3 nights = $210. Revenue projection: $200M (2008-2011).

---

### Output 1: Strategic Constitution (Product)

```markdown
---
version: 1.0.0
type: strategic
source: pitch-deck.md
pitch_deck_version: 1.0.0
---

# Product Constitution

**Source**: [`pitch-deck.md#solution`](../deck/pitch-deck.md#solution), [`pitch-deck.md#product`](../deck/pitch-deck.md#product)

## Principle 1: Dual Value Proposition

Guests save money compared to hotels, and hosts monetize unused space. Both sides must find clear value.

**Rationale**: Marketplace requires balanced incentives for guests and hosts to participate.

**Test**: User research shows ≥70% of guests cite "lower cost" and ≥70% of hosts cite "extra income" as primary motivation.

**Source**: [`pitch-deck.md#solution`](../deck/pitch-deck.md#solution) - "SAVE MONEY when traveling, MAKE MONEY when hosting"

## Principle 2: Local Authenticity

Prioritize cultural exchange and local experiences over generic hotel stays.

**Rationale**: Differentiation from hotels is core to value proposition ("disconnected from culture").

**Test**: Listings highlight local neighborhood features, host profiles emphasize local knowledge.

**Source**: [`pitch-deck.md#problem`](../deck/pitch-deck.md#problem) - "Hotels leave you disconnected from culture"
```

---

### Output 2: Feature Constitution (Booking System)

```markdown
---
version: 1.0.0
type: feature
source: pitch-deck.md
pitch_deck_version: 1.0.0
upstream:
  - company-constitution.md
  - product-constitution.md
  - business-constitution.md
---

# Feature 004: Booking System

**Upstream**: [`product-constitution.md#principle-1`](../memory/product-constitution.md#principle-1), [`business-constitution.md#principle-1`](../memory/business-constitution.md#principle-1)

## User Story 1 - Guest Books Listing (Priority: P1)

Traveler finds a listing, checks availability, and completes booking with payment.

**Acceptance Scenarios**:
1. **Given** guest views listing, **When** selects dates and clicks "Book", **Then** booking created with PENDING status
2. **Given** booking PENDING, **When** payment succeeds, **Then** booking becomes CONFIRMED

---

## Key Entities

### User (Traveler Role)

**Source**: Inferred from [`pitch-deck.md#solution`](../deck/pitch-deck.md#solution) - "travelers book rooms"

**Rationale**: Core user role for booking platform.

Attributes:
  - [TODO: Define user attributes - suggest: id, email, name, role]

Relationships:
  - has_many: Booking (inferred from "travelers book listings")

Constraints:
  - [TODO: Define validation rules - suggest: email format, role enum]

Lifecycle:
  - States: [TODO: Define user states - suggest: registered, verified]

### Booking

**Source**: Inferred from [`pitch-deck.md#business-model`](../deck/pitch-deck.md#business-model) - "10% commission on each transaction"

**Rationale**: Central entity representing guest-host transaction.

Attributes:
  - [TODO: Define attributes - suggest: id, listing_id, guest_id, check_in_date, check_out_date, total_price, commission, status]

Relationships:
  - belongs_to: User (guest)
  - belongs_to: Listing
  - has_one: Payment

Constraints:
  - [TODO: Define validation - suggest: check_in < check_out, total_price > 0]

Lifecycle:
  - States: [TODO: Define states - suggest: PENDING → CONFIRMED → ACTIVE → COMPLETED → CANCELLED]

---

## Success Criteria

- **SC-004-001**: Commission calculation accurate to 0.01% (verified against manual calculation for 10% rate)
  - **Source**: [`pitch-deck.md#business-model`](../deck/pitch-deck.md#business-model) - "10% commission"
  - **Type**: DERIVED
  - **Rationale**: Business model depends on 10% commission - calculation errors directly impact revenue
  - **Test**: Unit tests verify commission = booking_amount * 0.10 for all transaction types

- **SC-004-002**: Pricing display accurate to 2 decimal places
  - **Source**: [`pitch-deck.md#business-model`](../deck/pitch-deck.md#business-model) - "$70/night average"
  - **Type**: DERIVED
  - **Test**: Pricing calculations never lose precision beyond 2 decimals

- **SC-004-003**: [Success criterion supporting user conversion rate] ⚠️ PLACEHOLDER
  - **Source**: [`pitch-deck.md#business-model`](../deck/pitch-deck.md#business-model)
  - **Type**: PLACEHOLDER
  - **Business Goal**: Achieve sustainable booking volume
  - **Suggested Approaches**:
    - Booking completion time <5 minutes
    - Booking abandonment rate <20%
    - Payment success rate >95%
  - **Action Required**: Run `/bp.clarify --feature 004-booking-system` or manually specify criterion

---

## Feature Principles

### Principle 1: Transaction Integrity

All bookings must maintain financial accuracy (10% commission) and create audit trail for regulatory compliance.

**Source**: [`business-constitution.md#principle-1`](../memory/business-constitution.md#principle-1)

**Test**: Every booking has commission calculated, recorded, and reconcilable against financial reports.
```

---

## Workflow Integration

### Full BP-Kit → Speckit → Implementation Flow

```bash
# 1. Create pitch deck + constitutions
bpkit decompose --interactive  # or --from-file, --from-pdf

# 2. Validate quality (optional but recommended)
bpkit clarify                  # Resolve any ambiguities
bpkit analyze                  # Check traceability links
bpkit checklist                # Generate quality gates

# 3. Review generated constitutions
cat .specify/features/001-user-management.md

# 4. Use Speckit to implement features
/speckit.plan --constitution features/001-user-management.md
/speckit.tasks --constitution features/001-user-management.md
/speckit.implement

# 5. Update pitch deck with traction (after launch)
# [Edit pitch deck with product metrics]
bpkit sync --to-deck          # Regenerate pitch deck from learnings
```

---

## Common Scenarios

### Scenario 1: Founder with Business Idea

**Goal**: Go from idea to implementable feature specs in <1 hour.

```bash
bpkit decompose --interactive  # 15 min - answer Sequoia questions
bpkit analyze                  # 30 sec - validate links
bpkit checklist                # 10 sec - generate quality gates
# Review features, pick priority P1
/speckit.plan --constitution features/001-user-management.md  # 5 min
# Ready to implement
```

---

### Scenario 2: Startup with Existing Pitch Deck

**Goal**: Convert investor pitch deck to MVP specifications.

```bash
# Assume pitch-deck.md exists in Obsidian vault
bpkit decompose --from-file ~/Obsidian/Startup/pitch-deck.md
bpkit analyze --verbose        # Check extraction quality
# If issues found:
bpkit clarify --section business-model  # Fix specific section
# Continue to Speckit
```

---

### Scenario 3: Post-Launch Pivot

**Goal**: Update business model, regenerate constitutions, track changes.

```bash
# Edit pitch deck Business Model section (e.g., change from 10% to 15% commission)
vim .specify/deck/pitch-deck.md

# Re-decompose (detects existing files, prompts for overwrite)
bpkit decompose --from-file .specify/deck/pitch-deck.md

# System:
# - Detects version 1.0.0 → bumps to 1.1.0 (MINOR)
# - Flags affected features (payment, booking)
# - Creates changelog entry documenting pivot

# Review impact
cat .specify/changelog/2025-10-11-decompose-v1.1.0.md
# Shows: Business model changed, features 004-booking, 005-payment need review
```

---

## Dry-Run Mode (Preview Before Committing)

```bash
# Preview decomposition without writing files
bpkit decompose --from-file pitch-deck.md --dry-run

# Output:
# Would generate:
# - 4 strategic constitutions (company, product, market, business)
# - 7 feature constitutions (user-mgmt, listings, search, booking, payment, reviews, dashboard)
# - 42 traceability links
# - pitch-deck.md version 1.0.0
#
# No files written (dry-run mode)
```

---

## Success Indicators

After decomposition, you should have:
- ✅ 10-section pitch deck in `.specify/deck/pitch-deck.md`
- ✅ 4 strategic constitutions in `.specify/memory/`
- ✅ 5-10 feature constitutions in `.specify/features/`
- ✅ Changelog entry documenting decomposition
- ✅ All links validate (run `bpkit analyze`)
- ✅ Checklists generated (run `bpkit checklist`)

---

## Common Issues & Fixes

### Issue 1: "PDF extraction confidence low"

**Symptom**: Warning during `--from-pdf` mode: "Extraction confidence 65% (below 85% threshold)"

**Fix**:
```bash
# Review extracted pitch deck
cat .specify/deck/pitch-deck.md
# Look for [NEEDS REVIEW] markers
# Manually correct section boundaries
# Re-run decomposition
bpkit decompose --from-file .specify/deck/pitch-deck.md
```

---

### Issue 2: "Feature extraction found only 3 features (expected 5-10)"

**Symptom**: Warning: "Only 3 features detected in Product section (below minimum 5)"

**Fix**:
```bash
# Review Product and Solution sections for more detail
bpkit clarify --section product
# Add more feature details
# Re-decompose
```

---

### Issue 3: "Broken traceability links detected"

**Symptom**: `bpkit analyze` reports broken links

**Fix**:
```bash
# Analyze will show which links are broken
bpkit analyze --verbose
# Common cause: Manual edits to pitch deck changed section IDs
# Fix: Update constitution source links OR regenerate constitutions
bpkit decompose --from-file .specify/deck/pitch-deck.md
```

---

## Performance Expectations

Based on success criteria (SC-001, SC-005, SC-006):
- **Interactive mode**: 15 minutes total
- **From-file mode**: <2 minutes
- **From-PDF mode**: <2 minutes (+ extraction time ~30 seconds)

If decomposition takes longer, check:
- Pitch deck size (target: 10 sections, ~50 KB)
- Feature count (target: 5-10, not 20+)
- System resources (decomposition is CPU-bound)

---

## Next Steps

After successful decomposition:

1. **Validate**: Run `bpkit analyze` to check quality
2. **Refine**: Use `bpkit clarify` for ambiguous sections
3. **Implement**: Pick P1 feature, run `/speckit.plan --constitution features/001-*.md`
4. **Iterate**: Build MVP, gather learnings, update pitch deck, re-decompose

---

**Quickstart Complete**: 2025-10-11
**Full documentation**: See `spec.md`, `plan.md`, `research.md`, `data-model.md`
