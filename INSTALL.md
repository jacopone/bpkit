# BP-Kit Installation & Testing Guide

## 🏗️ NixOS Installation

### Option 1: Nix Development Shell (Recommended)

```bash
# Enter development environment
nix develop

# Install BP-Kit in editable mode
pip install -e .

# Verify installation
bpkit --help
```

### Option 2: Direct Nix Build

```bash
# Build the package
nix build

# Run directly
./result/bin/bpkit --help
```

### Option 3: Add to your system flake

Add to your `flake.nix`:

```nix
{
  inputs.bp-to-constitution.url = "path:/home/guyfawkes/bp-to-constitution";

  # In your packages:
  environment.systemPackages = [
    inputs.bp-to-constitution.packages.${system}.default
  ];
}
```

## 🧪 Testing the Implementation

### Test 1: Check Command Availability

```bash
nix develop
bpkit --help
```

Expected output:
```
╔══════════════════════════════════════════════════════════════╗
║              BP-Kit: Business Plan to Constitution           ║
║           Transform pitch decks into executable MVPs         ║
║                                                               ║
║  Companion tool to Speckit for business-driven development   ║
╚══════════════════════════════════════════════════════════════╝

Usage: bpkit [OPTIONS] COMMAND [ARGS]...
```

### Test 2: Interactive Mode (Dry Run)

```bash
# Test interactive Q&A without writing files
bpkit decompose --interactive --dry-run
```

This will:
1. Ask 10 Sequoia section questions
2. Show progress bar
3. Display summary
4. Preview decomposition (no files written)

### Test 3: Create Test Pitch Deck

Create a simple test pitch deck:

```bash
mkdir -p test-project/.specify/deck

cat > test-project/.specify/deck/pitch-deck.md << 'EOF'
---
version: 1.0.0
created: 2025-10-11
updated: 2025-10-11
type: pitch-deck
---

# Test Pitch Deck

## Company Purpose

AirBnB: Book rooms with locals, rather than hotels

## Problem

Price is an important concern for customers booking travel online. Hotels leave you disconnected from the city and its culture. No easy way exists to book a room with a local or become a host.

## Solution

SAVE MONEY when traveling. MAKE MONEY when hosting. SHARE CULTURE - local connection to the city.

## Why Now

Economic downturn makes affordable travel essential. Sharing economy trend growing. Trust systems now enable peer-to-peer transactions.

## Market Size

Travel industry: $500B annually. Online travel bookings: $150B. Target: budget-conscious travelers (30M potential users).

## Competition

Hotels.com, Expedia, Craigslist. We offer local authentic experiences vs generic hotel stays at better prices.

## Product

- User registration and profiles
- Listing management for hosts
- Search and discovery for guests
- Booking system with calendar
- Payment processing (10% commission)
- Review and rating system
- Host dashboard with analytics

## Business Model

10% commission on each transaction. Average booking: $70/night for 3 nights = $210 per booking. Revenue projection: $200M by 2011.

## Team

Brian Chesky (CEO) - RISD grad, designer. Joe Gebbia (CPO) - RISD grad, designer. Nathan Blecharczyk (CTO) - Harvard CS, engineer.

## Financials

Year 1: $1M revenue, break-even. Year 2: $20M revenue, 20% margin. Year 3: $200M revenue, 30% margin. Raising: $5M Series A.
EOF

echo "✓ Test pitch deck created"
```

### Test 4: Decompose from File

```bash
cd test-project
bpkit decompose --from-file .specify/deck/pitch-deck.md --dry-run
```

Expected output:
```
Parsing pitch deck: .specify/deck/pitch-deck.md
✓ Extracted 10 sections

Generating constitutions...

Decomposition Results

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Artifact Type              ┃ Count ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Strategic Constitutions    │     4 │
│ Feature Constitutions      │     7 │
│ Total Principles           │    XX │
│ Traceability Links         │    XX │
│ Entities Extracted         │    XX │
│ Success Criteria (Derived) │    XX │
│ Success Criteria (...)     │    XX │
└────────────────────────────┴───────┘

✓ Decomposition preview complete (no files written)
```

### Test 5: Full Decomposition (Write Files)

```bash
# Remove --dry-run to actually generate files
bpkit decompose --from-file .specify/deck/pitch-deck.md
```

This will create:
```
test-project/
└── .specify/
    ├── memory/
    │   ├── company-constitution.md
    │   ├── product-constitution.md
    │   ├── market-constitution.md
    │   └── business-constitution.md
    └── features/
        ├── 001-user-registration.md
        ├── 002-listing-management.md
        ├── 003-search-discovery.md
        ├── 004-booking-system.md
        ├── 005-payment-processing.md
        ├── 006-review-system.md
        └── 007-host-dashboard.md
```

### Test 6: Verify Generated Files

```bash
# Check strategic constitutions
bat test-project/.specify/memory/company-constitution.md

# Check feature constitutions
bat test-project/.specify/features/004-booking-system.md

# Verify structure
eza --tree test-project/.specify/
```

### Test 7: PDF Mode (Optional)

If you have a PDF pitch deck:

```bash
bpkit decompose --from-pdf ~/Downloads/pitch-deck.pdf --dry-run
```

Note: Requires `pymupdf` (already in flake.nix)

## 🔍 Validation Tests

### Test Sequoia Structure Validation

```bash
# Create invalid pitch deck (missing sections)
cat > test-invalid.md << 'EOF'
---
version: 1.0.0
---

# Incomplete Deck

## Problem
Some problem

## Solution
Some solution
EOF

# Should fail with validation error
bpkit decompose --from-file test-invalid.md
```

Expected: Error message listing missing Sequoia sections

### Test Help Documentation

```bash
# Main help
bpkit --help

# Command-specific help
bpkit decompose --help

# Other commands
bpkit check --help
bpkit analyze --help
bpkit clarify --help
```

## 🐛 Troubleshooting

### Issue: "bpkit: command not found"

```bash
# Ensure you're in nix develop shell
nix develop

# Reinstall in editable mode
pip install -e .
```

### Issue: "ImportError: No module named 'bpkit_cli'"

```bash
# Check PYTHONPATH
echo $PYTHONPATH

# Reinstall
pip uninstall bpkit-cli -y
pip install -e .
```

### Issue: "PyMuPDF not found" (PDF mode)

```bash
# Should already be in flake.nix, but if missing:
pip install pymupdf>=1.23.0
```

### Issue: Development environment issues

```bash
# Rebuild flake
nix flake update
nix develop --refresh
```

## 📊 Expected Test Results

After running all tests, you should see:

✅ **Command availability**: `bpkit --help` works
✅ **Interactive mode**: Q&A flow completes
✅ **File mode**: Parses existing markdown
✅ **PDF mode**: Extracts text from PDF
✅ **Validation**: Rejects invalid pitch decks
✅ **Generation**: Creates 4 strategic + 5-10 feature constitutions
✅ **Traceability**: All links formatted correctly
✅ **Dry-run**: Preview mode works

## 🚀 Next Steps After Testing

1. **Integrate with BP-Kit init**: Run `bpkit init` in a new project
2. **Validate quality**: Run `bpkit analyze` on generated constitutions
3. **Clarify ambiguities**: Run `bpkit clarify` on specific sections
4. **Start implementation**: Use `/speckit.plan` with generated features

## 📝 Development Workflow

```bash
# 1. Enter dev environment
nix develop

# 2. Make changes to src/

# 3. Test changes immediately (editable install)
bpkit decompose --interactive --dry-run

# 4. Run tests
pytest

# 5. Format and lint
black src/
ruff check src/

# 6. Commit changes
git add .
git commit -m "feat: your changes"
```
