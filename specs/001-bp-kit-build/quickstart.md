# Quickstart: BP-Kit Init Command

**Feature**: BP-Kit Init Command
**Target Audience**: Developers installing BP-Kit for the first time
**Time to Complete**: 2-5 minutes

---

## Prerequisites

Before installing BP-Kit, ensure you have:

- **Python 3.11+** installed ([Download](https://www.python.org/downloads/))
- **uv** package manager installed ([Installation](https://docs.astral.sh/uv/))
- **Network connection** (templates downloaded from GitHub)
- **Write permissions** in your project directory

**Optional**:
- Git repository initialized (for .gitignore support)
- Existing Speckit project (BP-Kit enhances Speckit but can work standalone)

---

## Installation

### Step 1: Install BP-Kit CLI

```bash
# Install from GitHub (recommended)
uv tool install bpkit-cli --from git+https://github.com/user/bp-kit.git

# Or use uvx to run without installing
uvx --from git+https://github.com/user/bp-kit.git bpkit init
```

### Step 2: Verify Installation

```bash
bpkit version
# Expected output:
# BP-Kit CLI version 0.1.0
# Companion tool to Speckit for business-driven development
```

---

## Usage

### Scenario 1: Install BP-Kit in Existing Speckit Project (Most Common)

If you already have a Speckit project with `.specify/` directory:

```bash
cd ~/my-speckit-project
bpkit init
```

**Expected Output**:
```
✓ Created .specify/deck/
✓ Created .specify/features/
✓ Created .specify/changelog/
✓ Created .specify/scripts/bp/
✓ Downloaded pitch-deck-template.md
✓ Downloaded strategic-constitution-template.md
✓ Downloaded feature-constitution-template.md
✓ Installed slash command: bp.decompose
✓ Installed slash command: bp.sync
✓ Created bash utilities

✨ BP-Kit successfully installed!

Next steps:
  1. Create your pitch deck: .specify/deck/pitch-deck.md
  2. Run decomposition: /bp.decompose --interactive
  3. Verify installation: bpkit check
```

**What Just Happened?**
- BP-Kit detected existing Speckit project (`.specify/` folder)
- Created BP-Kit-specific directories without conflicts
- Downloaded templates from GitHub
- Installed slash commands for AI agent workflows

---

### Scenario 2: Bootstrap New Project with BP-Kit

If starting from scratch (no Speckit yet):

```bash
mkdir my-startup
cd my-startup
bpkit init my-startup
```

**What Happens**:
- Creates both Speckit and BP-Kit directory structures
- Installs all templates
- Replaces `[PROJECT_NAME]` in templates with "my-startup"

**Directory Structure After Init**:
```
my-startup/
├── .specify/
│   ├── deck/             # Your pitch deck goes here
│   ├── features/         # Generated feature constitutions
│   ├── changelog/        # Pivot and change logs
│   ├── memory/           # Strategic constitutions
│   ├── scripts/bp/       # BP-Kit bash utilities
│   └── templates/        # Template files
│       ├── pitch-deck-template.md
│       ├── strategic-constitution-template.md
│       └── feature-constitution-template.md
└── .claude/
    └── commands/         # AI agent slash commands
        ├── bp.decompose.md
        └── bp.sync.md
```

---

### Scenario 3: Overwrite Existing BP-Kit Installation

If BP-Kit is already installed and you want to reinstall:

```bash
# Interactive prompt (default: No)
bpkit init
# Output: BP-Kit already installed. Overwrite? (y/N):

# Force overwrite without prompt
bpkit init --force
```

---

### Scenario 4: Install Without Git

If your project doesn't have Git initialized:

```bash
bpkit init
# Output: Git not detected. Create .gitignore for future use? (Y/n):
```

- Press Enter or type `y`: Creates `.gitignore` with BP-Kit entry
- Type `n`: Skips .gitignore creation, continues installation

---

## Verification

After installation, verify BP-Kit is working:

```bash
bpkit check
```

**Expected Output**:
```
Checking BP-Kit installation...

✓ Directory structure valid
  .specify/deck/       ✓
  .specify/features/   ✓
  .specify/changelog/  ✓
  .specify/scripts/bp/ ✓

✓ Templates present
  pitch-deck-template.md          ✓
  strategic-constitution-template.md ✓
  feature-constitution-template.md   ✓

✓ Slash commands installed
  /bp.decompose ✓
  /bp.sync      ✓

✓ No conflicts with Speckit

✅ All systems ready!
```

---

## Next Steps

### 1. Create Your Pitch Deck

```bash
# Copy template to create your pitch deck
cp .specify/templates/pitch-deck-template.md .specify/deck/pitch-deck.md

# Edit with your favorite editor
code .specify/deck/pitch-deck.md  # VS Code
vim .specify/deck/pitch-deck.md   # Vim
```

**Pro Tip**: Use the Sequoia Capital format. See `.specify/deck/pitch-deck-template.md` for structure.

### 2. Run Decomposition

Use the `/bp.decompose` slash command in your AI agent (Claude Code, Cursor, etc.):

```bash
# Interactive mode (recommended for first time)
/bp.decompose --interactive

# Or from file
/bp.decompose --from-file .specify/deck/pitch-deck.md
```

**What This Does**:
- Analyzes your pitch deck
- Generates 4 strategic constitutions (company, product, market, business)
- Generates 5-10 feature constitutions (MVP features)
- Establishes traceability links

### 3. Build Features with Speckit

Use Speckit's workflow to implement features:

```bash
# Generate implementation plan
/speckit.plan --constitution .specify/features/001-user-management.md

# Generate tasks
/speckit.tasks --constitution .specify/features/001-user-management.md

# Implement feature
/speckit.implement
```

### 4. Track Changes

When product evolves, update constitutions and sync back to pitch deck:

```bash
# Update pitch deck with traction data
/bp.sync --to-deck
```

---

## Common Options

### `--project-name` / Positional Argument

Replace `[PROJECT_NAME]` placeholder in templates:

```bash
bpkit init AirBnB
bpkit init "My Cool Startup"
```

### `--force` / `-f`

Skip all prompts, overwrite existing files:

```bash
bpkit init --force
bpkit init my-project -f
```

**Use Cases**:
- CI/CD pipelines
- Scripted installations
- Resetting corrupted installations

---

## Troubleshooting

### Problem: Network Connection Failed

**Symptoms**:
```
✗ Failed to download pitch-deck-template.md
  Error: Network connection failed
```

**Solutions**:
1. Check internet connection: `ping raw.githubusercontent.com`
2. Verify GitHub status: https://status.github.com
3. Check firewall/proxy settings
4. Retry: `bpkit init`

**Advanced**: Use custom template URL:
```bash
export BPKIT_TEMPLATES_URL=https://my-mirror.com/bp-kit
bpkit init
```

---

### Problem: Permission Denied

**Symptoms**:
```
✗ Permission denied: .specify/deck/
  Error: Cannot create directory (insufficient permissions)
```

**Solutions**:
1. Check directory permissions: `ls -la`
2. Fix permissions: `chmod u+w .`
3. Verify you own the directory: `stat .`

**Don't**: Use sudo (BP-Kit doesn't need root)

---

### Problem: BP-Kit Already Installed

**Symptoms**:
```
BP-Kit already installed. Overwrite? (y/N):
```

**Solutions**:
- **Keep existing**: Press `n` or Enter
- **Overwrite**: Type `y` (WARNING: Loses custom edits)
- **Force overwrite**: `bpkit init --force`

**Tip**: Backup custom templates before overwriting:
```bash
cp .specify/templates/my-custom-template.md ~/backup/
bpkit init --force
```

---

### Problem: Invalid Project Name

**Symptoms**:
```
✗ Invalid project name: "My Project!!!"
Project names must contain only letters, numbers, hyphens, underscores
```

**Solutions**:
- Use valid characters: `bpkit init my-project`
- Avoid spaces: `bpkit init MyProject` (not "My Project")
- Avoid special characters: `bpkit init my_startup` (not "my-startup!")

---

### Problem: Rollback After Failure

**Symptoms**:
```
✗ Failed to download ...
Rolling back changes...
✓ Rollback complete
```

**What Happened**:
- Installation failed mid-process
- BP-Kit automatically deleted all created files/directories
- Your project is in the same state as before `bpkit init`

**Next Steps**:
1. Fix the underlying issue (network, permissions, etc.)
2. Retry: `bpkit init`

---

## Advanced Usage

### Custom Template URLs

Override template source for testing or forks:

```bash
export BPKIT_TEMPLATES_URL=https://github.com/myorg/custom-bp-kit/raw/main
bpkit init
```

### Disable Colors (CI/CD)

For log readability in CI/CD pipelines:

```bash
BPKIT_NO_COLOR=1 bpkit init
```

### Scripted Installation

Automate installation in scripts:

```bash
#!/bin/bash
set -e

# Install without prompts
bpkit init my-project --force

# Verify
bpkit check

echo "BP-Kit setup complete!"
```

---

## Getting Help

### Command Help

```bash
# General help
bpkit --help

# Command-specific help
bpkit init --help
bpkit check --help
```

### Documentation

- **README**: https://github.com/user/bp-kit#readme
- **Constitution**: `.specify/memory/constitution.md` (explains BP-Kit principles)
- **Templates**: `.specify/templates/` (examples and structure)

### Support

- **Issues**: https://github.com/user/bp-kit/issues
- **Discussions**: https://github.com/user/bp-kit/discussions

---

## Summary

**Quick Reference**:

```bash
# Install BP-Kit CLI
uv tool install bpkit-cli --from git+https://github.com/user/bp-kit.git

# Initialize BP-Kit (existing Speckit project)
cd my-project
bpkit init

# Initialize BP-Kit (new project with name)
bpkit init my-startup

# Force overwrite
bpkit init --force

# Verify installation
bpkit check

# Next steps
# 1. Create pitch deck: .specify/deck/pitch-deck.md
# 2. Decompose: /bp.decompose --interactive
# 3. Build features: /speckit.plan, /speckit.tasks, /speckit.implement
```

**Time Investment**:
- Installation: 5-30 seconds
- Verification: 2 seconds
- Creating pitch deck: 30-60 minutes
- Decomposition: 5-10 minutes
- Building first feature: 30-120 minutes

**ROI**: BP-Kit transforms your business plan into executable MVP specifications, enabling AI agents to build features directly from your vision. The closed feedback loop ensures your pitch deck stays synchronized with product reality.

---

**Ready to build?** Run `bpkit init` and start transforming your business plan into code!
