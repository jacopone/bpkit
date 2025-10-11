# Quickstart: BP-Kit Quality Commands

**Goal**: Learn how to use `/bp.clarify`, `/bp.analyze`, and `/bp.checklist` to improve constitution quality

**Time**: 15 minutes
**Prerequisites**: BP-Kit installed (`bpkit init` completed), pitch deck created

---

## Scenario 1: Clarify Vague Pitch Deck (5 minutes)

**When**: You've drafted a pitch deck but some sections feel incomplete

### Step 1: Run Clarification

```bash
# In Claude Code
/bp.clarify
```

**What happens**:
- System analyzes `.specify/deck/pitch-deck.md`
- Identifies up to 5 ambiguous sections
- Presents questions with suggested answers

**Example Output**:

```markdown
## Question 1: Competition

**Context**: Your Competition section mentions "traditional hotels" but lacks specifics

**What we need to know**: Who are your top 3 direct competitors and what is your specific advantage over each?

**Suggested Answers**:

| Option | Answer | Implications |
|--------|--------|--------------|
| A | Airbnb, Vrbo, Booking.com - advantage is local authenticity | Positions as marketplace competitor |
| B | Traditional hotel chains - advantage is lower prices | Positions as budget alternative |
| C | Custom answer | Provide your own |

**Your choice**: _
```

### Step 2: Provide Answers

```bash
# Type your responses
Q1: A, Q2: Custom - Unit economics: CAC $50, LTV $300, 3 month payback, Q3: B
```

### Step 3: Verify Updates

```bash
# Check updated pitch deck
cat .specify/deck/pitch-deck.md
```

**Result**: Sections updated with your answers, version bumped to 1.0.1

---

## Scenario 2: Validate Constitutions After Decomposition (3 minutes)

**When**: You've run `/bp.decompose` and want to check for errors

### Step 1: Run Analysis

```bash
/bp.analyze
```

**What happens**:
- Scans all constitutions in `.specify/memory/` and `.specify/features/`
- Validates traceability links
- Detects conflicts and coverage gaps

**Example Output (No Issues)**:

```markdown
✅ All systems ready - no issues found

**Analysis Summary**:
- Strategic constitutions: 4
- Feature constitutions: 7
- Links validated: 42
- Errors: 0
- Warnings: 0

**Next steps**: Run /bp.checklist to generate quality gates
```

**Example Output (Issues Found)**:

```markdown
⚠️ Issues detected - see report for details

**Errors** (2):
1. ERROR: features/003-search.md:45 references company-constitution.md#principle-5 which does not exist
2. ERROR: features/005-payment.md:67 references ../memory/business-constitution.md#revenue-model (broken section ID)

**Warnings** (1):
1. CONFLICT: product-constitution.md#principle-2 (Mobile-first UX) contradicts market-constitution.md#principle-1 (Desktop enterprise users)

**Report saved to**: .specify/changelog/2025-10-10-analyze-report.md

**Next steps**: Fix errors, then re-run /bp.analyze
```

### Step 2: Fix Issues

```bash
# Open reported files and fix broken links
# Re-run analysis
/bp.analyze
```

**Result**: Clean analysis report ready for next phase

---

## Scenario 3: Generate Quality Checklists (2 minutes)

**When**: Analysis passes and you want structured quality review

### Step 1: Generate Checklists

```bash
/bp.checklist
```

**What happens**:
- Creates checklist for each constitution
- Strategic constitutions get 10 items
- Feature constitutions get 15 items
- Files written to `.specify/checklists/`

**Example Output**:

```markdown
✅ Checklists generated for 11 constitutions

**Created**:
- .specify/checklists/company-constitution.md (10 items)
- .specify/checklists/product-constitution.md (10 items)
- .specify/checklists/market-constitution.md (10 items)
- .specify/checklists/business-constitution.md (10 items)
- .specify/checklists/001-user-management.md (15 items)
- .specify/checklists/002-listing-management.md (15 items)
- .specify/checklists/003-search-discovery.md (15 items)
- ... (4 more)

**Next steps**: Review checklists and check off items as you validate
```

### Step 2: Review Checklists

```bash
# Open first checklist
cat .specify/checklists/company-constitution.md
```

**Example Checklist**:

```markdown
# Quality Checklist: Company Constitution

**Constitution**: [company-constitution.md](../memory/company-constitution.md)
**Type**: Strategic
**Generated**: 2025-10-10

## Traceability (4 items)

- [ ] All principles have measurable outcomes
- [ ] Each principle links back to pitch deck section
- [ ] Version properly tracked in frontmatter
- [ ] At least 3 downstream features reference this constitution

## Quality (3 items)

- [ ] No implementation details in principles
- [ ] Principles are testable and unambiguous
- [ ] Rationale explains 'why' for each principle

## Completeness (3 items)

- [ ] Examples include both compliant and violation cases
- [ ] Amendment process documented
- [ ] Review cycle defined
```

### Step 3: Check Off Items

```bash
# Manually edit checklist and change [ ] to [x]
# Example:
- [x] All principles have measurable outcomes
- [x] Each principle links back to pitch deck section
```

### Step 4: Check Completion Status

```bash
/bp.checklist --report
```

**Example Output**:

```markdown
📊 Checklist Completion Report

| Constitution | Completion | Remaining |
|--------------|------------|-----------|
| company-constitution | 100% ✅ | 0 |
| product-constitution | 80% | 2 |
| market-constitution | 90% | 1 |
| business-constitution | 100% ✅ | 0 |
| 001-user-management | 86% | 2 |
| 002-listing-management | 93% | 1 |
| 003-search-discovery | 100% ✅ | 0 |
| ... | ... | ... |

**Overall**: 89% complete (8 items remaining)

**Next steps**: Complete remaining items, then ready for /speckit.implement
```

---

## Scenario 4: Focus Clarification on Specific Section (2 minutes)

**When**: You know one section needs work

### Step 1: Target Specific Section

```bash
/bp.clarify --section=business-model
```

**What happens**:
- Only analyzes the `business-model` section
- Asks targeted questions about CAC, LTV, margins, revenue streams

**Example Output**:

```markdown
## Question 1: Unit Economics

**Context**: Business Model section mentions "commission-based" but lacks specifics

**What we need to know**: What are your target unit economics?

**Suggested Answers**:

| Option | Answer | Implications |
|--------|--------|--------------|
| A | CAC: $50, LTV: $300, Margin: 15%, Payback: 3 months | Strong unit economics |
| B | CAC: $100, LTV: $250, Margin: 10%, Payback: 6 months | Tighter margins |
| C | Custom answer | Provide your own |

**Your choice**: _
```

---

## Scenario 5: Dry Run Clarification (2 minutes)

**When**: You want to see questions without modifying pitch deck

### Step 1: Preview Questions

```bash
/bp.clarify --dry-run
```

**What happens**:
- Shows questions and suggested answers
- Does NOT update pitch deck
- Does NOT bump version

**Use case**: Review what clarifications are needed before committing

---

## Complete Workflow Example

**Full BP-Kit Quality Workflow** (15 minutes start to finish):

```bash
# 1. Create pitch deck
# Edit .specify/deck/pitch-deck.md

# 2. Clarify ambiguities
/bp.clarify
# Answer questions interactively

# 3. Decompose into constitutions
/bp.decompose --interactive
# Answer feature prioritization questions

# 4. Validate consistency
/bp.analyze
# Fix any errors reported

# 5. Generate quality gates
/bp.checklist
# Review and check off items

# 6. Verify readiness
/bp.checklist --report
# Ensure 100% completion

# 7. Implement with AI agents
/speckit.plan --constitution features/001-user-management.md
/speckit.tasks --constitution features/001-user-management.md
/speckit.implement
```

---

## Common Issues & Solutions

### Issue: "No constitutions found"

**Symptom**: `/bp.analyze` or `/bp.checklist` reports no constitutions

**Solution**:
```bash
# Run decompose first
/bp.decompose
```

### Issue: "Checklist already exists"

**Symptom**: `/bp.checklist` says files exist

**Solution**:
```bash
# Overwrite existing checklists
/bp.checklist --force
```

### Issue: "Broken link detected"

**Symptom**: `/bp.analyze` reports `features/003-search.md:45 references company#principle-5 which does not exist`

**Solution**:
```bash
# Option 1: Fix the link
# Edit features/003-search.md line 45
# Change principle-5 to correct principle ID

# Option 2: Add missing principle
# Edit company-constitution.md
# Add principle-5 if it should exist

# Re-validate
/bp.analyze
```

### Issue: "Version mismatch"

**Symptom**: `/bp.analyze` warns constitution references old pitch deck version

**Solution**:
```bash
# Sync constitutions with updated pitch deck
/bp.sync --from deck

# Re-analyze
/bp.analyze
```

### Issue: "Conflict detected"

**Symptom**: Two constitutions have contradictory principles

**Solution**:
```bash
# Review both principles
cat .specify/memory/product-constitution.md
cat .specify/memory/market-constitution.md

# Decide:
# Option A: Align principles (one is wrong)
# Option B: Document intentional trade-off in changelog
```

---

## Tips & Best Practices

### Tip 1: Run `/bp.clarify` BEFORE `/bp.decompose`

**Why**: Better input = better output. Clear pitch deck generates strong constitutions.

### Tip 2: Use `--dry-run` to preview

**Why**: See what questions would be asked without committing changes.

### Tip 3: Fix errors before running `/bp.checklist`

**Why**: Checklists assume analysis passes. Fix structural issues first.

### Tip 4: Track checklist completion in PRs

**Why**: Use `/bp.checklist --report` output to show constitution quality in PR descriptions.

### Tip 5: Re-run `/bp.analyze` after manual edits

**Why**: Catch new issues introduced by manual constitution changes.

---

## Integration with Speckit

**How BP-Kit Quality Commands Enhance Speckit Workflow**:

```
Traditional Speckit:
1. Write spec manually
2. /speckit.plan
3. /speckit.tasks
4. /speckit.implement

Enhanced with BP-Kit Quality:
1. Write pitch deck
2. /bp.clarify ← Quality command
3. /bp.decompose (generates specs)
4. /bp.analyze ← Quality command
5. /bp.checklist ← Quality command
6. /speckit.plan --constitution features/001-*.md
7. /speckit.tasks
8. /speckit.implement
```

**Result**: Higher quality specs with less manual work.

---

## Next Steps

- **Learn more**: Read [data-model.md](./data-model.md) for entity details
- **Contribute**: Suggest new checklist items or clarification patterns
- **Integrate**: Use quality commands in your team's workflow

**Questions?** See [contracts/slash-commands.yaml](./contracts/slash-commands.yaml) for complete command reference.
