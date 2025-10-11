# BP-Kit Sync Command

Synchronize constitutions when pitch deck is updated.

## Usage

```bash
bpkit sync [OPTIONS]
```

## What This Does

1. Detects changes in pitch deck since last decomposition
2. Identifies affected constitutions based on traceability links
3. Prompts for updates to affected constitutions
4. Updates version numbers and timestamps
5. Validates bidirectional traceability

## When to Use

- After updating your pitch deck
- Before running Speckit workflows
- To verify constitution-to-pitch-deck alignment

## Example

```bash
# Sync after pitch deck update
bpkit sync

# Preview changes without updating
bpkit sync --dry-run
```
