---
description: "Generate quality validation checklists for all constitutions"
---

# /bp.checklist - Quality Validation Checklists

Execute the `/bp.checklist` command to generate structured validation checklists for all constitutions, or view completion status.

## What This Command Does

### Generate Mode (default)
1. **Scans** `.specify/memory/` and `.specify/features/` for constitutions
2. **Determines** type (strategic vs feature)
3. **Loads** appropriate Jinja2 template
4. **Renders** template with constitution-specific context
5. **Writes** checklist to `.specify/checklists/{constitution-name}.md`
6. **Displays** summary of generated checklists

### Report Mode (--report flag)
1. **Scans** `.specify/checklists/` for existing checklists
2. **Parses** each checklist and counts checked items
3. **Calculates** completion percentage
4. **Displays** table with completion status
5. **Shows** overall readiness assessment

## Usage

```bash
# Generate checklists for all constitutions
bpkit checklist

# View completion status
bpkit checklist --report

# Overwrite existing checklists
bpkit checklist --force
```

## Parameters

- `--report` (optional): Show completion status instead of generating new checklists
- `--force` (optional): Overwrite existing checklists

## Output

**Generate Mode** (success):
```
✅ Checklists generated for 11 constitutions

Location: .specify/checklists/
Generated: 11 new
Skipped: 0 existing

Next steps:
• Review checklists and check off items as you validate
• Run bpkit checklist --report to track completion progress
• Once 100% complete, ready for /speckit.implement
```

**Report Mode** (incomplete):
```
📊 Checklist Completion Report

Constitution                | Completion | Remaining | Status
─────────────────────────────────────────────────────────────
company-constitution        | 100%       | 0         | ✅
product-constitution        | 80%        | 2         | ⚠️
market-constitution         | 90%        | 1         | ⚠️
business-constitution       | 100%       | 0         | ✅
001-user-management         | 86%        | 2         | ⚠️
002-listing-management      | 93%        | 1         | ⚠️
...

Overall: 89% complete (8 items remaining)

⚠️ Work in progress - 6 checklists incomplete

Complete remaining items to validate constitutional quality.

Next steps:
• Review and check off remaining validation items
• Re-run bpkit checklist --report to track progress
• Once 100%, ready for /speckit.implement
```

**Report Mode** (all complete):
```
✅ All checklists 100% complete!

All constitutions have been validated.

Ready for implementation:
• Run /speckit.plan for each feature
• Or run /speckit.implement to build features with AI agents
```

## Checklist Templates

### Strategic Constitution Checklist (10 items)

**Traceability** (4 items):
- All principles have measurable outcomes
- Each principle links back to pitch deck section
- Version properly tracked in frontmatter
- At least 3 downstream features reference this constitution

**Quality** (3 items):
- No implementation details in principles
- Principles are testable and unambiguous
- Rationale explains 'why' for each principle

**Completeness** (3 items):
- Examples include both compliant and violation cases
- Amendment process documented
- Review cycle defined

### Feature Constitution Checklist (15 items)

**Traceability** (5 items):
- All user stories have acceptance criteria
- Success criteria are measurable and technology-agnostic
- Feature links to at least 1 strategic principle
- Feature principles (FP1-FPX) all have upstream sources
- Version properly tracked in frontmatter

**Quality** (5 items):
- Data model entities are clearly defined
- Entity relationships documented
- No [NEEDS CLARIFICATION] markers remain
- Principles are testable and unambiguous
- Security/privacy considerations addressed

**Completeness** (5 items):
- MVP boundaries are explicit (IN/OUT scope)
- Dependencies on other features listed
- Edge cases identified
- Non-functional requirements specified
- Ready for /speckit.plan

## Workflow Integration

**Recommended sequence**:
1. Create pitch deck → Run `/bp.clarify` → Resolve ambiguities
2. Run `/bp.decompose` → Generate constitutions
3. Run `/bp.analyze` → Validate consistency
4. **Run `/bp.checklist`** → Generate quality gates ← YOU ARE HERE
5. Review and check off items
6. Run `/bp.checklist --report` → Verify 100% completion
7. Proceed to `/speckit.implement`

## How to Use Checklists

1. **Generate**: Run `bpkit checklist`
2. **Open**: Navigate to `.specify/checklists/{constitution-name}.md`
3. **Review**: Read each validation criterion
4. **Check**: Change `- [ ]` to `- [x]` for completed items
5. **Track**: Run `bpkit checklist --report` to see progress
6. **Repeat**: Until all checklists are 100% complete

**Example editing**:
```markdown
## Traceability (4 items)

- [x] All principles have measurable outcomes  ← Changed from [ ] to [x]
- [x] Each principle links back to pitch deck section
- [ ] Version properly tracked in frontmatter  ← Still needs work
- [ ] At least 3 downstream features reference this constitution
```

## Performance

Target: <5 seconds to generate all checklists (typical: 11 constitutions)

Actual performance depends on:
- Number of constitutions (typical: 4 strategic + 7 feature)
- Filesystem performance

## Error Handling

**No constitutions found**:
```
❌ Error: No constitutions found.

Run /bp.decompose first to generate constitutions from pitch deck.
```

**Checklist already exists**:
```
⚠️ Skipping company-constitution.md (already exists)

Use --force to overwrite existing checklists.
```

**No checklists in report mode**:
```
⚠️ No checklists found.

Run bpkit checklist first to generate checklists.
```

**Template not found**:
```
❌ Error: Template not found: strategic-checklist.j2

Ensure BP-Kit is properly installed with templates.
```

## File Structure

Generated checklists follow this structure:
```markdown
# Quality Checklist: {constitution-name}

**Constitution**: [{constitution-name}.md](../memory/{constitution-name}.md)
**Type**: Strategic | Feature
**Generated**: YYYY-MM-DD
**Completion**: XX%

## Traceability (N items)

- [ ] Item 1
- [ ] Item 2
...

## Quality (N items)

- [ ] Item 1
- [ ] Item 2
...

## Completeness (N items)

- [ ] Item 1
- [ ] Item 2
...

---

**Total Items**: N
**Next Step**: Check off items as you validate, then run `/bp.checklist --report`
```

## Customization

Checklists are generated from Jinja2 templates:
- `src/bpkit_cli/templates/strategic-checklist.j2` (10 items)
- `src/bpkit_cli/templates/feature-checklist.j2` (15 items)

To customize:
1. Edit template files to add/remove/modify items
2. Run `bpkit checklist --force` to regenerate all checklists
3. New checklists will use updated template

## Common Issues & Solutions

### Issue: Skipped because already exists

**Symptom**: `Skipping company-constitution.md (already exists)`

**Solution**:
```bash
# Option 1: Overwrite all
bpkit checklist --force

# Option 2: Delete specific checklist first
rm .specify/checklists/company-constitution.md
bpkit checklist
```

### Issue: Report shows 0% but you've checked items

**Symptom**: Manually checked items but report still shows 0%

**Solution**:
- Ensure you used lowercase `[x]` not `[X]` (parser accepts both but some markdown renderers don't)
- Check there are no spaces inside brackets: `- [x]` not `- [ x]`
- Re-run `bpkit checklist --report`

### Issue: Checklist missing items

**Symptom**: Template seems incomplete

**Solution**:
1. Check template files exist in `src/bpkit_cli/templates/`
2. Compare against contract specification (10 items for strategic, 15 for feature)
3. If template is outdated, update and run `--force`

## Integration with Speckit

**How BP-Kit Checklists Enhance Speckit Workflow**:

```
Traditional Speckit:
1. Write spec manually
2. /speckit.plan
3. /speckit.tasks
4. /speckit.implement

Enhanced with BP-Kit Checklists:
1. Write pitch deck
2. /bp.clarify
3. /bp.decompose (generates specs)
4. /bp.analyze
5. /bp.checklist ← Quality gates
6. Validate all checklists (manual review)
7. /speckit.plan --constitution features/001-*.md
8. /speckit.tasks
9. /speckit.implement
```

**Result**: Higher confidence in specification quality before AI implementation.

## Related Commands

- `/bp.decompose` - Generate constitutions from pitch deck (run before checklist)
- `/bp.analyze` - Validate constitutional consistency (run before checklist)
- `/bp.clarify` - Resolve pitch deck ambiguities (run before decompose)

## References

- Spec: [specs/002-bp-kit-quality/spec.md](../../specs/002-bp-kit-quality/spec.md)
- Contract: [specs/002-bp-kit-quality/contracts/slash-commands.yaml](../../specs/002-bp-kit-quality/contracts/slash-commands.yaml)
- Quickstart: [specs/002-bp-kit-quality/quickstart.md](../../specs/002-bp-kit-quality/quickstart.md)
