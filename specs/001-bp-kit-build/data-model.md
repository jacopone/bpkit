# Data Model: BP-Kit Init Command

**Feature**: BP-Kit Init Command
**Date**: 2025-10-10
**Purpose**: Define entities, relationships, and state transitions

---

## Core Entities

### 1. Template

**Purpose**: Represents a BP-Kit template file to be downloaded and installed.

**Attributes**:
| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| name | str | Required, unique | Template filename (e.g., "pitch-deck-template.md") |
| source_url | str | Required, valid URL | GitHub raw content URL |
| destination_path | Path | Required, relative to project root | Where to install (e.g., ".specify/templates/pitch-deck-template.md") |
| content | str | Optional (None until downloaded) | Template file content |
| type | TemplateType | Required | Enum: MARKDOWN, BASH_SCRIPT, SLASH_COMMAND |
| size_bytes | int | Optional | Content size for validation |

**Validation Rules**:
- `name` must end with `.md` or `.sh` extension
- `source_url` must use `https://` protocol
- `destination_path` must be within `.specify/` or `.claude/commands/` directories
- `content` is None initially, populated after download
- `size_bytes` must be < 1MB (sanity check)

**Relationships**:
- Template → InstallationState (many-to-one): Multiple templates tracked by one installation
- Template → Directory (many-to-one): Each template installed into a directory

**Example**:
```python
Template(
    name="pitch-deck-template.md",
    source_url="https://raw.githubusercontent.com/user/bp-kit/main/templates/pitch-deck-template.md",
    destination_path=Path(".specify/templates/pitch-deck-template.md"),
    content=None,  # Populated after download
    type=TemplateType.MARKDOWN,
    size_bytes=None
)
```

---

### 2. Directory

**Purpose**: Represents a directory to be created during installation.

**Attributes**:
| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| path | Path | Required, unique, relative to project root | Directory path (e.g., ".specify/deck/") |
| exists_before_install | bool | Required | True if existed before `bpkit init` ran |
| created_by_bpkit | bool | Computed | True if created by current installation |
| is_empty | bool | Computed | True if directory contains no files |

**Validation Rules**:
- `path` must be within `.specify/` hierarchy
- `path` must be a directory, not a file
- Cannot delete `path` if `exists_before_install` is True (rollback safety)

**Relationships**:
- Directory → Template (one-to-many): One directory contains multiple templates
- Directory → InstallationState (many-to-one): Multiple directories tracked by one installation

**State Transitions**:
```
NONEXISTENT --[mkdir]-> CREATED_EMPTY --[write files]-> CREATED_WITH_FILES
     ↑                        |                              |
     |                        |                              |
     +-------[rollback]-------+------------------------------+
```

**Example**:
```python
Directory(
    path=Path(".specify/deck/"),
    exists_before_install=False,  # Didn't exist, we created it
    created_by_bpkit=True,
    is_empty=True
)
```

---

### 3. InstallationState

**Purpose**: Tracks the overall state of BP-Kit installation for rollback and validation.

**Attributes**:
| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| status | InstallationStatus | Required | Enum: UNINSTALLED, INSTALLING, INSTALLED, FAILED |
| project_dir | Path | Required | Project root directory (default: cwd) |
| is_speckit_project | bool | Required | True if `.specify/` existed before init |
| files_created | List[Path] | Required, default=[] | Files created during installation (for rollback) |
| dirs_created | List[Path] | Required, default=[] | Directories created during installation (for rollback) |
| conflicts | List[str] | Required, default=[] | List of conflicts detected (Speckit file overwrites) |
| error_message | str | Optional | Error details if status=FAILED |
| installed_at | datetime | Optional | Timestamp when installation completed |

**Validation Rules**:
- `status` must transition in order: UNINSTALLED → INSTALLING → (INSTALLED | FAILED)
- `conflicts` must be empty for installation to proceed (unless --force)
- `files_created` and `dirs_created` only track paths created by this installation
- `error_message` required if `status` is FAILED

**Relationships**:
- InstallationState → Template (one-to-many): Tracks multiple templates
- InstallationState → Directory (one-to-many): Tracks multiple directories

**State Transitions**:
```
UNINSTALLED --[detect_conflicts]-> INSTALLING --[download_success]-> INSTALLED
                                        |
                                        +---[download_failed]-> FAILED
                                        |
                                        +---[permission_denied]-> FAILED --[rollback]-> UNINSTALLED
```

**Example**:
```python
InstallationState(
    status=InstallationStatus.INSTALLING,
    project_dir=Path.cwd(),
    is_speckit_project=True,
    files_created=[
        Path(".specify/templates/pitch-deck-template.md"),
        Path(".claude/commands/bp.decompose.md"),
    ],
    dirs_created=[
        Path(".specify/deck/"),
        Path(".specify/features/"),
    ],
    conflicts=[],
    error_message=None,
    installed_at=None
)
```

---

### 4. GitRepository

**Purpose**: Represents Git repository state for .gitignore handling.

**Attributes**:
| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| exists | bool | Required | True if `.git/` directory detected |
| gitignore_path | Path | Required | Path to `.gitignore` file (may not exist) |
| gitignore_exists | bool | Computed | True if .gitignore file exists |
| has_bpkit_entry | bool | Computed | True if .gitignore contains `.specify/deck/*.pdf` |

**Validation Rules**:
- `exists` determined by checking for `.git/` directory
- `gitignore_path` always `.gitignore` relative to project root
- Cannot modify .gitignore if it's read-only (permission check)

**Relationships**:
- GitRepository → InstallationState (one-to-one): Git state influences installation decisions

**State Transitions**:
```
NO_GIT --[git init]-> GIT_NO_IGNORE --[create .gitignore]-> GIT_WITH_IGNORE --[append entry]-> GIT_COMPLETE
```

**Example**:
```python
GitRepository(
    exists=False,  # No .git/ directory
    gitignore_path=Path(".gitignore"),
    gitignore_exists=False,
    has_bpkit_entry=False
)
```

---

## Enums

### TemplateType
```python
from enum import Enum

class TemplateType(str, Enum):
    MARKDOWN = "markdown"       # .md files (pitch-deck, constitutions)
    BASH_SCRIPT = "bash"        # .sh files (bp-common.sh, decompose-setup.sh)
    SLASH_COMMAND = "command"   # .md files in .claude/commands/
```

### InstallationStatus
```python
from enum import Enum

class InstallationStatus(str, Enum):
    UNINSTALLED = "uninstalled"  # BP-Kit not installed
    INSTALLING = "installing"     # Installation in progress
    INSTALLED = "installed"       # Successfully installed
    FAILED = "failed"             # Installation failed (rollback triggered)
```

---

## Relationships Diagram

```
InstallationState (1)
    │
    ├──> Template (N)
    │       └──> Directory (1)
    │
    ├──> Directory (N)
    │
    └──> GitRepository (1)
```

---

## State Machine: Installation Lifecycle

```
┌─────────────┐
│ UNINSTALLED │
└──────┬──────┘
       │
       │ bpkit init
       │
       ▼
┌─────────────────┐
│ Detect Conflicts │
└──────┬──────────┘
       │
       ├─ Conflicts found → Prompt user → [No] → EXIT
       │
       └─ No conflicts or --force
          │
          ▼
┌──────────────┐
│  INSTALLING  │ ◄───────────┐
└──────┬───────┘             │
       │                     │
       ├─ Create directories │
       ├─ Download templates │  (Each step tracks changes)
       ├─ Write files        │
       ├─ Handle .gitignore  │
       │                     │
       ▼                     │
    SUCCESS?                 │
       │                     │
       ├─ YES ──> ┌──────────┴─┐
       │          │  INSTALLED  │
       │          └─────────────┘
       │
       └─ NO ──> ┌─────────┐
                 │ FAILED  │
                 └────┬────┘
                      │
                      │ Rollback
                      ▼
                 ┌─────────────┐
                 │ UNINSTALLED │
                 └─────────────┘
```

---

## Validation Matrix

| Entity | Validation Check | Failure Behavior |
|--------|------------------|------------------|
| Template | source_url is reachable | Retry 3x → Rollback → Error |
| Template | content size < 1MB | Rollback → Error "Template too large" |
| Directory | parent directory exists | Create parents recursively |
| Directory | write permissions | Rollback → Error "Permission denied: {path}" |
| InstallationState | conflicts list empty | Prompt user or require --force |
| GitRepository | .gitignore writable | Skip .gitignore modification, warn user |

---

## Example Installation Flow

```python
# 1. Initialize state
state = InstallationState(
    status=InstallationStatus.UNINSTALLED,
    project_dir=Path.cwd(),
    is_speckit_project=Path(".specify").exists(),
)

# 2. Check for conflicts
if state.is_speckit_project:
    # Detect BP-Kit already installed
    if is_bpkit_installed():
        if not force and not prompt_overwrite():
            raise InstallationCancelled()

# 3. Transition to INSTALLING
state.status = InstallationStatus.INSTALLING

# 4. Create directories
for dir_path in [".specify/deck", ".specify/features", ".specify/changelog"]:
    dir_obj = Directory(path=Path(dir_path), exists_before_install=dir_path.exists())
    if not dir_obj.exists_before_install:
        dir_path.mkdir(parents=True)
        state.dirs_created.append(dir_path)

# 5. Download and install templates
for template in TEMPLATES:
    template.content = download_template(template.source_url)  # May raise NetworkError
    template.destination_path.write_text(template.content)
    state.files_created.append(template.destination_path)

# 6. Handle Git
git_repo = GitRepository(
    exists=Path(".git").exists(),
    gitignore_path=Path(".gitignore"),
)
if not git_repo.exists:
    if prompt_gitignore():
        create_gitignore(git_repo.gitignore_path)
        state.files_created.append(git_repo.gitignore_path)

# 7. Success
state.status = InstallationStatus.INSTALLED
state.installed_at = datetime.now()
```

---

## Persistence

**Storage**: No persistent database. State exists only during `bpkit init` execution.

**Detection** (for `bpkit check`): Check file existence:
- `.specify/deck/` directory → BP-Kit installed
- `.specify/templates/pitch-deck-template.md` → Templates installed
- `.claude/commands/bp.decompose.md` → Slash commands installed

**Rationale**: Installation state is ephemeral. After installation completes, BP-Kit relies on file existence checks, not a state database.

---

## Constraints Summary

1. **Template Constraints**:
   - Max size: 1MB per file
   - Allowed extensions: `.md`, `.sh`
   - Source URLs must use HTTPS

2. **Directory Constraints**:
   - Must be within `.specify/` hierarchy
   - Cannot delete if existed before installation

3. **Installation Constraints**:
   - No Speckit file overwrites (FR-006)
   - Must complete in < 30 seconds (SC-001)
   - 95% success rate on first try (SC-003)

4. **Rollback Constraints**:
   - Only delete files/directories created by this installation
   - LIFO deletion order
   - Never delete non-empty directories

---

## Future Extensions (Out of Scope for v1)

- **Template versioning**: Track template version, support upgrades
- **Partial installation recovery**: Resume failed installations
- **Template caching**: Cache in `~/.config/bpkit/cache/`
- **Conflict resolution**: Merge strategies for custom templates
- **Installation history**: Log all installations in `.specify/changelog/`
