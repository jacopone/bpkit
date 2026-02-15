# BPKit

Transform business plans into executable MVP specifications for AI coding agents.

BPKit decomposes a pitch deck into structured "constitutions" -- strategic and feature-level specs that AI agents (Claude Code, Cursor, etc.) can implement directly. As the product evolves, constitutions update bidirectionally: strategy flows down into features, and product learnings flow back up into the pitch deck.

## The Closed Loop

```
Business Plan (pitch deck)
    --> bpkit decompose -->
Strategic Constitutions (company, product, market, business)
    -->
Feature Constitutions (5-10 per MVP, each with stories + data models + success criteria)
    --> AI agents build -->
Working MVP
    --> metrics + learnings -->
Updated Constitutions
    --> bpkit sync --to-deck -->
Updated Pitch Deck (with traction data)
```

## Quick Start

### Install and initialize

```bash
uv tool install bpkit-cli    # or: pip install bpkit-cli

mkdir my-startup && cd my-startup
bpkit init my-startup
```

### Decompose a business plan

```bash
bpkit decompose --interactive       # Walk through pitch deck questions
bpkit decompose --from-file pitch.md  # From existing markdown
bpkit decompose --from-pdf deck.pdf   # From PDF
```

This generates:
- `.specify/deck/pitch-deck.md` -- canonical pitch deck
- `.specify/memory/` -- 4 strategic constitutions
- `.specify/features/` -- 5-10 feature constitutions

### Build with AI agents

Hand feature constitutions to any AI coding agent. Each one contains everything needed: user stories, data models, constraints, and success criteria.

### Sync after iteration

```bash
bpkit sync --check      # Validate consistency
bpkit sync --to-deck    # Constitutions changed -- regenerate deck
bpkit sync --from deck  # Deck changed (pivot) -- update constitutions
```

## Commands

| Command | Purpose |
|---------|---------|
| `bpkit init` | Initialize BPKit in a project |
| `bpkit decompose` | Pitch deck to constitutions |
| `bpkit sync` | Bidirectional sync (deck and constitutions) |
| `bpkit clarify` | Identify and resolve pitch deck ambiguities |
| `bpkit analyze` | Validate consistency and traceability |
| `bpkit checklist` | Generate quality validation checklists |
| `bpkit check` | Verify installation and project structure |

## Directory Structure

```
.specify/
  deck/pitch-deck.md            # Source of truth
  memory/                       # 4 strategic constitutions
    company-constitution.md
    product-constitution.md
    market-constitution.md
    business-constitution.md
  features/                     # 5-10 feature constitutions
    001-user-management.md
    002-listing-management.md
    ...
  changelog/                    # Pivot and learning records
  templates/                    # Constitution and deck templates
  FEATURE_MAP.md                # Dependency graph + build order
```

## How It Works

Constitutions sit between strategy and code. A strategic constitution captures principles like "target budget-conscious travelers" or "10% commission on bookings." Feature constitutions translate those into buildable specs with user stories, entity definitions, and measurable success criteria.

Every principle traces back to its source in the pitch deck. Every feature links to the strategic constitutions it implements. When something changes at any level, `bpkit sync` propagates updates in both directions.

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## License

MIT
