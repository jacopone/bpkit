# Manual Testing Guide: BP-Kit Quality Commands

**Status**: Ready for manual testing
**Prerequisites**: Feature 001 (`/bp.decompose`) implementation complete

---

## T040: Run Workflow on Real Pitch Deck

**Goal**: Validate all three quality commands work end-to-end with real data

### Prerequisites

1. **Install BP-Kit CLI**:
```bash
cd /home/guyfawkes/bp-to-constitution
uv pip install -e .
```

2. **Create test project directory**:
```bash
mkdir -p /tmp/bpkit-test
cd /tmp/bpkit-test
bpkit init bpkit-test
```

3. **Create sample pitch deck**:
```bash
# Option 1: Use AirBnB example (create manually)
# Copy Sequoia template and fill with AirBnB example from README

# Option 2: Use /bp.decompose --interactive (when Feature 001 complete)
```

### Test Scenario 1: /bp.clarify

**Steps**:
1. Create pitch deck with intentional vague sections:
```bash
cat > .specify/deck/pitch-deck.md << 'EOF'
---
version: 1.0.0
---

# AirBnB Pitch Deck

## Company Purpose
[TBD - need to clarify]

## Problem
Traditional hotels are expensive and generic.

## Solution
Platform for renting spare rooms.

## Business Model
Commission-based [NEEDS DETAILS]
EOF
```

2. Run clarify:
```bash
bpkit clarify
```

3. **Expected**:
   - Detects 2-3 vague sections (Company Purpose, Business Model)
   - Asks questions with suggested answers
   - Updates deck in-place
   - Bumps version to 1.0.1

4. **Validate**:
```bash
# Check version bump
grep "version:" .specify/deck/pitch-deck.md

# Check changelog
cat .specify/changelog/$(date +%Y-%m-%d)-clarify*.md

# Verify no [TBD] markers remain
grep -i "TBD\|NEEDS" .specify/deck/pitch-deck.md
```

### Test Scenario 2: /bp.analyze

**Prerequisites**: Create sample constitutions (manual or via Feature 001)

**Steps**:
1. Create strategic constitutions:
```bash
mkdir -p .specify/memory
cat > .specify/memory/company-constitution.md << 'EOF'
---
version: 1.0.0
type: strategic
---

# Company Constitution

**Source**: [pitch-deck.md#company-purpose](../deck/pitch-deck.md#company-purpose)

## Principle 1: Democratize Hospitality
[Content...]
EOF

cat > .specify/memory/product-constitution.md << 'EOF'
---
version: 1.0.0
type: strategic
---

# Product Constitution

**Source**: [pitch-deck.md#solution](../deck/pitch-deck.md#solution)

## Principle 1: Local Authenticity
[Content...]
EOF
```

2. Create feature constitution with intentional broken link:
```bash
mkdir -p .specify/features
cat > .specify/features/001-user-management.md << 'EOF'
---
version: 1.0.0
type: feature
---

# Feature 001: User Management

**Upstream**: [company-constitution.md#principle-5](../memory/company-constitution.md#principle-5)
                ^--- BROKEN: principle-5 does not exist

## User Stories
[Content...]
EOF
```

3. Run analyze:
```bash
bpkit analyze
```

4. **Expected**:
   - Reports 1 error: broken link to principle-5
   - Suggests available sections
   - Saves report to changelog
   - Exit code 1 (error detected)

5. Fix broken link:
```bash
sed -i 's/principle-5/principle-1/' .specify/features/001-user-management.md
```

6. Re-run analyze:
```bash
bpkit analyze
```

7. **Expected**:
   - Clean report, no errors
   - Exit code 0

### Test Scenario 3: /bp.checklist

**Steps**:
1. Generate checklists:
```bash
bpkit checklist
```

2. **Expected**:
   - Creates `.specify/checklists/company-constitution.md` (10 items)
   - Creates `.specify/checklists/product-constitution.md` (10 items)
   - Creates `.specify/checklists/001-user-management.md` (15 items)

3. Verify checklist content:
```bash
cat .specify/checklists/company-constitution.md
```

4. **Expected**:
   - 3 sections: Traceability, Quality, Completeness
   - All items unchecked `- [ ]`
   - Links to constitution file

5. Manually check off items:
```bash
# Edit checklist, change some [ ] to [x]
sed -i '0,/- \[ \]/s//- [x]/' .specify/checklists/company-constitution.md
sed -i '0,/- \[ \]/s//- [x]/' .specify/checklists/company-constitution.md
```

6. Run completion report:
```bash
bpkit checklist --report
```

7. **Expected**:
   - Table showing completion percentages
   - company-constitution: ~20% (2/10 items checked)
   - Other checklists: 0%
   - Overall status: incomplete

### Test Scenario 4: Complete Workflow

**Full end-to-end test** (15 minutes):

```bash
# 1. Start fresh
rm -rf /tmp/bpkit-test
mkdir /tmp/bpkit-test && cd /tmp/bpkit-test
bpkit init bpkit-test

# 2. Create pitch deck with vagueness
# [Manual - copy AirBnB example with some [TBD] sections]

# 3. Clarify
bpkit clarify
# Answer questions interactively

# 4. Decompose (when Feature 001 ready)
# bpkit decompose --interactive

# 5. Analyze
bpkit analyze --verbose

# 6. Fix any errors
# [Manual edits based on analysis report]

# 7. Re-analyze
bpkit analyze

# 8. Generate checklists
bpkit checklist

# 9. Review checklists
ls -la .specify/checklists/

# 10. Check off items
# [Manual review and checking]

# 11. Verify completion
bpkit checklist --report

# Expected: All commands work seamlessly together
```

### Performance Expectations (T041)

**Target performance** (from contract):
- `/bp.clarify`: < 10 seconds (typical: 5-8s for full deck analysis)
- `/bp.analyze`: < 2 seconds (typical: 1-1.5s for 11 constitutions, 42 links)
- `/bp.checklist`: < 5 seconds (typical: 2-3s for 11 constitutions)

**Measure**:
```bash
time bpkit clarify --dry-run
time bpkit analyze
time bpkit checklist
```

### Success Criteria

**All scenarios pass if**:
- ✅ No Python exceptions or crashes
- ✅ Rich formatting displays correctly
- ✅ Files created in correct locations
- ✅ Changelog entries generated
- ✅ Version bumping works correctly
- ✅ Links validated accurately
- ✅ Checklists match template item counts (10 strategic, 15 feature)
- ✅ Report mode calculates completion % correctly
- ✅ Performance meets targets

---

## Current Status

**Status**: Implementation complete, awaiting Feature 001 for full testing

**Why T040 deferred**:
- Feature 001 (`/bp.decompose`) not yet implemented
- No sample pitch deck → constitutions pipeline available
- Commands are fully implemented but need real data for end-to-end test

**Recommendation**:
1. Complete Feature 001 first
2. Then run this manual testing guide
3. Document any edge cases discovered

**Alternative**: Create minimal test fixtures manually (pitch deck + 2-3 constitutions) for smoke testing

---

## Next Steps After Manual Testing

1. **Document findings**: Update VALIDATION.md with test results
2. **Report bugs**: Create issues for any unexpected behavior
3. **Update docs**: Enhance quickstart.md based on real usage
4. **Benchmark**: Record actual performance numbers (T041)
5. **Sign off**: Mark T040 complete in tasks.md

---

**Maintainer Note**: This guide should be executed after Feature 001 is complete. Until then, T040 is considered "implementation complete, testing deferred."
