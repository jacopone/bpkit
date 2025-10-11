# BP-Kit Decompose Command

Decompose a Sequoia-format pitch deck into constitutional principles for AI implementation.

## Usage

```bash
bpkit decompose [OPTIONS]
```

## Options

- `--interactive`: Interactive Q&A mode - create pitch deck from scratch
- `--from-file PATH`: Path to existing markdown pitch deck file
- `--from-pdf PATH`: Path to PDF pitch deck to extract and decompose
- `--dry-run`: Preview decomposition without writing files
- `--force`: Overwrite existing constitutions without prompting

## What This Does

1. Analyzes pitch deck sections (Problem, Solution, Market, Product, etc.)
2. Generates 4 strategic constitutions (company, product, market, business)
3. Generates 5-10 feature constitutions with bidirectional traceability
4. Creates version-tracked links between pitch deck and constitutions

## Example

```bash
# Interactive mode
bpkit decompose --interactive

# From existing file
bpkit decompose --from-file .specify/deck/pitch-deck.md

# From PDF
bpkit decompose --from-pdf ~/Downloads/pitch-deck.pdf --dry-run
```
