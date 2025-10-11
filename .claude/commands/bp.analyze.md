---
description: "Validate constitutional consistency and traceability"
---

# /bp.analyze - Constitutional Consistency Validation

Execute the `/bp.analyze` command to validate consistency and traceability across all constitutions after running `/bp.decompose`.

## What This Command Does

1. **Validates** all traceability links (pitch deck ← strategic ← features)
2. **Detects** conflicting principles across strategic constitutions
3. **Checks** coverage gaps (pitch deck sections not referenced)
4. **Validates** version consistency (constitutions vs pitch deck)
5. **Detects** circular dependencies between features
6. **Identifies** orphaned principles (no downstream references)
7. **Generates** analysis report with errors/warnings/info
8. **Saves** report to `.specify/changelog/`

## Usage

```bash
# Standard analysis
bpkit analyze

# Verbose mode (show all details)
bpkit analyze --verbose

# Auto-fix mode (version mismatches only)
bpkit analyze --fix
```

## Parameters

- `--verbose` / `-v` (optional): Show detailed analysis including valid links
- `--fix` (optional): Attempt to auto-fix simple issues (version mismatches only)

## Output

**Success** (no errors):
```
✅ All systems ready - no issues found

Strategic constitutions: 4
Feature constitutions: 7
Links validated: 42
Errors: 0
Warnings: 0

Next steps:
• Run /bp.checklist to generate quality gates
• Or proceed directly to /speckit.implement
```

**Issues Found**:
```
❌ Issues detected - 2 errors found

Errors (blocking issues):
  • [ERROR] features/003-search.md:45: Section '#principle-5' not found in company-constitution.md
    💡 Available sections: principle-1, principle-2, principle-3, principle-4
  • [ERROR] features/005-payment.md:67: Target file does not exist: ../memory/business-constitution.md
    💡 Create file or update link

Warnings (should fix):
  • [WARNING] Potential conflict: product-constitution#principle-2 mentions 'mobile' but market-constitution#principle-1 mentions 'desktop'
    💡 Review principles and align or document intentional trade-off

See report for details: AR-20251010-123456
```

## Validation Rules

### Broken Link (ERROR)
- **Severity**: ERROR (blocks progression)
- **Detection**: Target file does not exist OR section ID not found
- **Message**: `ERROR: {source_file}:{line} references {target}#{section} which does not exist`
- **Auto-fix**: Not supported
- **Next step**: Fix manually, then re-run `/bp.analyze`

### Conflict (WARNING)
- **Severity**: WARNING (non-blocking)
- **Detection**: Contradictory keywords in principles (mobile/desktop, b2b/b2c, etc.)
- **Message**: `CONFLICT: {file1}#{principle1} mentions '{keyword1}' but {file2}#{principle2} mentions '{keyword2}'`
- **Auto-fix**: Not supported
- **Suggestion**: Review principles and align or document intentional trade-off

### Coverage Gap (WARNING)
- **Severity**: WARNING (non-blocking)
- **Detection**: Pitch deck section not referenced by any strategic constitution
- **Message**: `COVERAGE GAP: pitch-deck.md#{section} not referenced by any constitution`
- **Suggestion**: Add principle to appropriate strategic constitution

### Version Mismatch (WARNING)
- **Severity**: WARNING (non-blocking)
- **Detection**: Constitution references old pitch deck version
- **Message**: `VERSION MISMATCH: {constitution} is v{old_version} but pitch deck is v{new_version}`
- **Auto-fix**: Supported with `--fix` flag
- **Suggestion**: Run `/bp.sync --from deck` to update versions

### Circular Dependency (WARNING)
- **Severity**: WARNING (non-blocking)
- **Detection**: Feature A depends on Feature B which depends on Feature A
- **Message**: `CIRC: Circular dependency detected: Feature A → Feature B → Feature A`
- **Suggestion**: Review feature dependencies and break the cycle

### Orphaned Principle (INFO)
- **Severity**: INFO (informational only)
- **Detection**: Strategic principle has no downstream references from features
- **Message**: `INFO: {constitution}#{principle} has no downstream references`

## Workflow Integration

**Recommended sequence**:
1. Create pitch deck → Run `/bp.clarify` → Resolve ambiguities
2. **Run `/bp.decompose`** → Generate constitutions
3. **Run `/bp.analyze`** → Validate consistency ← YOU ARE HERE
4. Fix any errors/warnings
5. Run `/bp.checklist` → Generate quality gates

## Performance

Target: <2 seconds for 10 constitutions with 100+ links

Actual performance depends on:
- Number of constitutions (typical: 4 strategic + 5-10 feature)
- Number of links per constitution (typical: 5-10)
- Filesystem performance

## Error Handling

**No constitutions found**:
```
❌ Error: No constitutions found.

Run /bp.decompose first to generate constitutions from pitch deck.
```

**Pitch deck not found**:
```
❌ Error: Pitch deck not found at .specify/deck/pitch-deck.md

Run bpkit init to create project structure.
```

**Parse error**:
```
⚠️  Warning: Failed to parse company-constitution.md: Invalid YAML frontmatter

Skipping file and continuing analysis.
```

## Changelog

Analysis reports are saved to:
```
.specify/changelog/YYYY-MM-DD-analyze-report.md
```

Report includes:
- Report ID (AR-YYYYMMDD-HHMMSS)
- Timestamp
- Pitch deck version
- Constitutions analyzed count
- All errors with file paths and line numbers
- All warnings with suggestions
- All info items
- Next steps

## Example Analysis Report

```markdown
# Analysis Report

**Report ID**: AR-20251010-123456
**Date**: 2025-10-10 12:34:56
**Pitch Deck Version**: v1.0.1
**Constitutions Analyzed**: 11
**Status**: ❌ FAILING

## Summary

- **Errors**: 2 (blocking issues)
- **Warnings**: 3 (non-blocking issues)
- **Info**: 5 (informational)

## Errors

1. [ERROR] features/003-search.md:45: Section '#principle-5' not found in company-constitution.md
   - **Suggestion**: Available sections: principle-1, principle-2, principle-3, principle-4

2. [ERROR] features/005-payment.md:67: Target file does not exist: ../memory/business-constitution.md
   - **Suggestion**: Create file or update link

## Warnings

1. [WARNING] Potential conflict: product-constitution#principle-2 mentions 'mobile' but market-constitution#principle-1 mentions 'desktop'
   - **Suggestion**: Review principles and align or document intentional trade-off

## Next Steps

- Fix all errors before proceeding
- Re-run `/bp.analyze` to validate fixes
```

## Common Issues & Solutions

### Issue: Broken link to pitch deck section

**Symptom**: `ERROR: features/001.md:10 references pitch-deck.md#invalid-section which does not exist`

**Solution**:
1. Check valid section IDs in pitch deck: `company-purpose`, `problem`, `solution`, `market-potential`, `competition`, `business-model`, `team`, `go-to-market`
2. Update link in `features/001.md` line 10 to use correct section ID
3. Re-run `/bp.analyze`

### Issue: Version mismatch after clarify

**Symptom**: `WARNING: company-constitution is v1.0.0 but pitch deck is v1.0.1`

**Solution**:
```bash
# Option 1: Auto-fix (updates version references)
bpkit analyze --fix

# Option 2: Manual sync (regenerates constitutions)
/bp.sync --from deck

# Then re-validate
bpkit analyze
```

### Issue: Circular dependency between features

**Symptom**: `WARNING: Circular dependency: 001-auth → 002-users → 001-auth`

**Solution**:
1. Review feature dependencies in both constitutions
2. Extract shared functionality into a third feature
3. OR remove one direction of the dependency
4. Re-run `/bp.analyze`

### Issue: Coverage gap for new pitch deck section

**Symptom**: `WARNING: pitch-deck.md#financials not referenced by any constitution`

**Solution**:
1. Decide which strategic constitution should cover this section
2. Add principle to that constitution referencing `pitch-deck.md#financials`
3. Re-run `/bp.analyze`

## Related Commands

- `/bp.decompose` - Generate constitutions from pitch deck (run before analyze)
- `/bp.clarify` - Resolve pitch deck ambiguities (run before decompose)
- `/bp.checklist` - Generate quality validation checklists (run after analyze)
- `/bp.sync` - Bidirectional sync between pitch deck and constitutions

## References

- Spec: [specs/002-bp-kit-quality/spec.md](../../specs/002-bp-kit-quality/spec.md)
- Contract: [specs/002-bp-kit-quality/contracts/slash-commands.yaml](../../specs/002-bp-kit-quality/contracts/slash-commands.yaml)
- Quickstart: [specs/002-bp-kit-quality/quickstart.md](../../specs/002-bp-kit-quality/quickstart.md)
