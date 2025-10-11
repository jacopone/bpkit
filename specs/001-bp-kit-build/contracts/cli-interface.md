# CLI Interface Contract: bpkit init

**Purpose**: Define the command-line interface contract for `bpkit init` command.

---

## Command Signature

```bash
bpkit init [PROJECT_NAME] [OPTIONS]
```

---

## Arguments

### `PROJECT_NAME` (Optional Positional)

- **Type**: String
- **Description**: Name of the project to initialize BP-Kit for
- **Constraints**:
  - Alphanumeric characters, hyphens, underscores only
  - 1-50 characters
  - Used to replace `[PROJECT_NAME]` placeholder in templates
- **Default**: None (templates use `[PROJECT_NAME]` as-is)
- **Examples**:
  - `bpkit init my-startup`
  - `bpkit init AirBnB`
  - `bpkit init "My Cool Project"`

---

## Options

### `--force` / `-f`

- **Type**: Boolean flag
- **Description**: Skip all confirmation prompts, overwrite existing files
- **Default**: False
- **Behavior**:
  - Skips overwrite prompt when BP-Kit already installed
  - Skips Git .gitignore prompt
  - Assumes "yes" to all questions
  - Used for CI/CD automation
- **Example**:
  ```bash
  bpkit init --force
  bpkit init my-project -f
  ```

---

## Exit Codes

| Code | Meaning | Trigger |
|------|---------|---------|
| 0 | Success | Installation completed successfully |
| 1 | General error | Network failure, permission denied, unknown error |
| 2 | User cancelled | User answered "No" to overwrite prompt or pressed Ctrl+C |
| 3 | Validation error | Invalid arguments (e.g., PROJECT_NAME contains invalid characters) |

---

## Output Contract

### Success Output (Exit Code 0)

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

Documentation: https://github.com/user/bp-kit#readme
```

### Error Output (Exit Code 1)

**Network Failure:**
```
✗ Failed to download pitch-deck-template.md
  Error: Network connection failed
  URL: https://raw.githubusercontent.com/user/bp-kit/main/templates/pitch-deck-template.md

Rolling back changes...
✓ Rollback complete

Troubleshooting:
  • Check your internet connection
  • Verify GitHub is accessible: https://status.github.com
  • Try again in a few moments

Run 'bpkit init' to retry installation.
```

**Permission Denied:**
```
✗ Permission denied: .specify/deck/
  Error: Cannot create directory (insufficient permissions)

Rolling back changes...
✓ Rollback complete

Troubleshooting:
  • Check write permissions for current directory
  • Run: chmod u+w .
  • Or use sudo (not recommended)

Run 'bpkit init' to retry installation.
```

**Already Installed (No --force):**
```
BP-Kit already installed. Overwrite? (y/N): n

Installation cancelled. No changes made.

To force overwrite, run: bpkit init --force
```

### User Cancellation (Exit Code 2)

```
Installation cancelled by user.

No changes made.
```

### Validation Error (Exit Code 3)

```
✗ Invalid project name: "My Project!!!"

Project names must:
  • Contain only letters, numbers, hyphens, underscores
  • Be 1-50 characters long

Examples:
  bpkit init my-project
  bpkit init MyProject
  bpkit init my_cool_startup
```

---

## Interactive Prompts

### Overwrite Confirmation

**Trigger**: BP-Kit already installed AND --force not provided

```
BP-Kit already installed. Overwrite? (y/N):
```

- **Input**: Single character (y/n/Y/N) or Enter
- **Default**: N (No)
- **Behavior**:
  - `y` or `Y`: Proceed with overwrite
  - `n` or `N` or Enter: Cancel installation, exit code 2
  - Ctrl+C: Cancel installation, exit code 2

### Git .gitignore Prompt

**Trigger**: No `.git/` directory detected AND --force not provided

```
Git not detected. Create .gitignore for future use? (Y/n):
```

- **Input**: Single character (y/n/Y/N) or Enter
- **Default**: Y (Yes)
- **Behavior**:
  - `y` or `Y` or Enter: Create .gitignore file
  - `n` or `N`: Skip .gitignore creation, continue installation
  - Ctrl+C: Skip .gitignore, continue installation (non-critical prompt)

---

## Environment Variables

### `BPKIT_TEMPLATES_URL`

- **Type**: String (URL)
- **Description**: Override base URL for template downloads
- **Default**: `https://raw.githubusercontent.com/user/bp-kit/main`
- **Use Case**: Testing, custom forks, offline mirrors
- **Example**:
  ```bash
  export BPKIT_TEMPLATES_URL=https://my-cdn.com/bp-kit
  bpkit init
  ```

### `BPKIT_NO_COLOR`

- **Type**: Boolean (1/0 or true/false)
- **Description**: Disable colored output
- **Default**: False (colors enabled)
- **Use Case**: CI/CD logs, terminals without color support
- **Example**:
  ```bash
  BPKIT_NO_COLOR=1 bpkit init
  ```

---

## File System Side Effects

**Directories Created** (if not exist):
- `.specify/deck/`
- `.specify/features/`
- `.specify/changelog/`
- `.specify/scripts/bp/`
- `.specify/templates/` (if not exist)
- `.claude/commands/` (if not exist)

**Files Created** (12 total per SC-006):
1. `.specify/templates/pitch-deck-template.md`
2. `.specify/templates/strategic-constitution-template.md`
3. `.specify/templates/feature-constitution-template.md`
4. `.claude/commands/bp.decompose.md`
5. `.claude/commands/bp.sync.md`
6. `.specify/scripts/bp/bp-common.sh`
7. `.specify/scripts/bp/decompose-setup.sh`
8. `.specify/deck/README.md` (placeholder)
9. `.specify/features/README.md` (placeholder)
10. `.specify/changelog/README.md` (placeholder)
11. `.specify/scripts/bp/README.md` (placeholder)
12. `.gitignore` (if user confirms OR --force used)

**Files Modified** (if exist):
- `.gitignore` (append `.specify/deck/*.pdf` entry if not present)

**Files Never Modified**:
- Any existing Speckit files (FR-006 validation)
- User content in `.specify/memory/`, `.specify/features/`
- Any `/speckit.*` slash commands

---

## Performance Contract

**Timing Requirements** (from SC-001):
- **Target**: < 30 seconds total
- **Expected**: 3-8 seconds for typical installations

**Breakdown**:
| Phase | Expected Time | Max Time |
|-------|---------------|----------|
| Speckit detection | < 10ms | 50ms |
| Conflict detection | < 50ms | 200ms |
| User prompts (if any) | 2-5s | N/A (user-dependent) |
| Directory creation | < 10ms | 100ms |
| Template downloads (7 files) | 1-3s | 10s |
| File writes | < 50ms | 200ms |
| Validation | < 10ms | 50ms |
| **Total** | **3-8s** | **30s** |

---

## Compatibility Contract

**Supported Platforms**:
- Linux (x86_64, aarch64)
- macOS (Intel, Apple Silicon)
- Windows (WSL2, native Python)

**Python Version**: 3.11+

**Terminal Requirements**:
- Unicode support (for ✓ ✗ ✨ symbols)
- ANSI color codes (or set `BPKIT_NO_COLOR=1`)
- Minimum width: 60 characters

**Network Requirements**:
- HTTPS support (TLS 1.2+)
- Access to `raw.githubusercontent.com`
- Bandwidth: ~70 KB download

---

## Test Scenarios

### Scenario 1: Fresh Install in Empty Directory

```bash
$ cd /tmp/new-project
$ bpkit init MyStartup
✓ Created .specify/deck/
...
✨ BP-Kit successfully installed!
$ echo $?
0
```

### Scenario 2: Install in Existing Speckit Project

```bash
$ cd ~/my-speckit-project
$ ls .specify/
memory/  templates/
$ bpkit init
✓ Created .specify/deck/
...
✨ BP-Kit successfully installed!
$ ls .specify/
deck/  features/  memory/  templates/
```

### Scenario 3: Overwrite with --force

```bash
$ bpkit init
BP-Kit already installed. Overwrite? (y/N): n
Installation cancelled.
$ bpkit init --force
✓ Overwriting existing BP-Kit installation...
...
✨ BP-Kit successfully installed!
```

### Scenario 4: Network Failure

```bash
$ bpkit init
✓ Created .specify/deck/
✗ Failed to download pitch-deck-template.md
Rolling back changes...
✓ Rollback complete
$ echo $?
1
```

### Scenario 5: Git Not Detected

```bash
$ cd /tmp/no-git-project
$ bpkit init
Git not detected. Create .gitignore for future use? (Y/n): y
✓ Created .gitignore
...
✨ BP-Kit successfully installed!
```

---

## Security Contract

**Template Source Validation**:
- Only download from HTTPS URLs
- Validate SSL certificates (no `--insecure`)
- Reject templates > 1MB (prevent DOS)

**Path Traversal Prevention**:
- Template destination paths must be within `.specify/` or `.claude/`
- Reject paths containing `..` or absolute paths
- Use `Path.resolve()` to canonicalize paths

**Prompt Injection Prevention**:
- Sanitize PROJECT_NAME before template replacement
- No shell command execution from user input
- Validate characters: `[a-zA-Z0-9_-]` only

---

## Rollback Contract

**Triggers**:
- Network error during download
- Disk full during file write
- Permission denied
- Unexpected exception

**Behavior**:
- Delete all files created by this installation (tracked in `files_created`)
- Delete all directories created by this installation (tracked in `dirs_created`)
- LIFO order: Last created, first deleted
- Only delete empty directories
- Never delete pre-existing files/directories
- Display "Rolling back changes..." message
- Display "✓ Rollback complete" on success

**Example**:
```
✓ Created .specify/deck/
✓ Downloaded pitch-deck-template.md
✗ Failed to download strategic-constitution-template.md

Rolling back changes...
  Deleted .specify/templates/pitch-deck-template.md
  Deleted .specify/deck/
✓ Rollback complete

Error: Network connection failed
```

---

## Version Contract

**Command Version Display**:
```bash
$ bpkit version
BP-Kit CLI version 0.1.0

Companion tool to Speckit for business-driven development
Homepage: https://github.com/yourusername/bp-kit
```

**Help Output**:
```bash
$ bpkit init --help

Usage: bpkit init [PROJECT_NAME] [OPTIONS]

Initialize BP-Kit templates in a Speckit project.

This command sets up the BP-Kit directory structure and templates in an
existing Speckit project, enabling business plan decomposition.

Arguments:
  PROJECT_NAME  Name of the project to initialize BP-Kit for [optional]

Options:
  -f, --force   Overwrite existing BP-Kit setup
  --help        Show this message and exit

Examples:
  bpkit init                    # Install in current directory
  bpkit init my-startup         # Install with project name
  bpkit init --force            # Force overwrite without prompts
```
