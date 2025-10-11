---
description: "Analyze pitch deck for ambiguities and prompt user for clarifications"
---

# /bp.clarify - Pitch Deck Clarification

Execute the `/bp.clarify` command to identify vague or incomplete sections in your pitch deck and interactively resolve them.

## What This Command Does

1. **Analyzes** `.specify/deck/pitch-deck.md` for ambiguities
2. **Identifies** incomplete sections (missing required content, placeholder text, vague phrases)
3. **Prioritizes** up to 5 highest-impact clarification questions (HIGH > MEDIUM > LOW)
4. **Prompts** user interactively with suggested answers
5. **Updates** pitch deck sections with user responses
6. **Bumps** pitch deck version (PATCH increment)
7. **Logs** operation to `.specify/changelog/`

## Usage

```bash
# Clarify entire pitch deck
bpkit clarify

# Focus on specific section
bpkit clarify --section=business-model

# Preview questions without updating
bpkit clarify --dry-run
```

## Parameters

- `--section` (optional): Section ID to focus on (e.g., `business-model`, `competition`, `market-potential`)
- `--dry-run` (optional): Show questions without updating pitch deck

## Output

**Success** (ambiguities found):
```
✅ Pitch deck clarified - 3 sections updated

Version bumped: v1.0.0 → v1.0.1

Next steps:
• Run /bp.decompose to generate or regenerate constitutions
• Run /bp.analyze to validate constitutional consistency
```

**Success** (no ambiguities):
```
✅ No clarifications needed - pitch deck is complete

All sections have sufficient detail. Ready to run /bp.decompose.
```

**Warning** (already decomposed):
```
⚠️  Pitch deck already decomposed into constitutions.
Clarifications will update the pitch deck, but you'll need to re-run
/bp.decompose to regenerate constitutions.
```

## Question Format

Each question includes:
- **Context**: Which section needs clarification
- **Priority**: HIGH (scope/financials), MEDIUM (strategy), or LOW (details)
- **Suggested Answers**: Pre-populated options (A, B, C, ...) + custom answer option
- **Your Choice**: Select letter or enter custom text

Example question:
```
Question CLQ001
Section: competition
Priority: HIGH

Who are your top 3 direct competitors and what is your specific advantage over each?

Option  Answer
─────────────────────────────────────────────────────
A       Airbnb, Vrbo, Booking.com - advantage is local authenticity
B       Traditional hotel chains - advantage is lower prices
C       Custom answer

Select option (A, B, C) or enter custom answer: _
```

## Workflow Integration

**Recommended sequence**:
1. Create pitch deck → **Run `/bp.clarify`** → Resolve ambiguities
2. Run `/bp.decompose` → Generate constitutions
3. Run `/bp.analyze` → Validate consistency
4. Run `/bp.checklist` → Generate quality gates

## Error Handling

**Pitch deck not found**:
```
❌ Error: Pitch deck not found at .specify/deck/pitch-deck.md

Run bpkit init to create project structure.
```

**Invalid section parameter**:
```
❌ Error: Section 'invalid-section' not found in pitch deck

Valid sections: company-purpose, problem, solution, why-now, market-potential,
competition, business-model, team, go-to-market
```

## Changelog

Clarification operations are logged to:
```
.specify/changelog/YYYY-MM-DD-clarify-<section>.md  # Focused clarification
.specify/changelog/YYYY-MM-DD-clarify-full.md       # Full deck clarification
```

Log includes:
- Timestamp
- Sections updated
- Version bump (old → new)
- Next steps

## Section-Specific Questions

The command generates targeted questions based on section type:

| Section | Question Focus |
|---------|----------------|
| **competition** | Top 3 competitors + specific advantage |
| **business-model** | Unit economics (CAC, LTV, margins, payback) |
| **market-potential** | TAM, SAM, market share targets |
| **problem** | Specific problem + who experiences it |
| **solution** | Core solution + 10x better factor |
| **why-now** | Timing catalyst + what changed |
| **company-purpose** | Mission in one sentence |
| **team** | Unique qualifications |
| **go-to-market** | GTM strategy + customer acquisition |

## Performance

Target: <10 seconds for typical pitch deck with 8 sections

## Related Commands

- `/bp.decompose` - Generate constitutions from pitch deck (run after clarify)
- `/bp.analyze` - Validate constitutional consistency
- `/bp.checklist` - Generate quality validation checklists

## References

- Spec: [specs/002-bp-kit-quality/spec.md](../../specs/002-bp-kit-quality/spec.md)
- Contract: [specs/002-bp-kit-quality/contracts/slash-commands.yaml](../../specs/002-bp-kit-quality/contracts/slash-commands.yaml)
- Quickstart: [specs/002-bp-kit-quality/quickstart.md](../../specs/002-bp-kit-quality/quickstart.md)
