# Research: BP-Kit Init Command

**Feature**: BP-Kit Init Command
**Date**: 2025-10-10
**Purpose**: Resolve technical unknowns and establish implementation patterns

---

## 1. Template Download Patterns

### Decision: Synchronous httpx with retry logic

**Rationale**:
- Small number of templates (7 files total) - async overhead not justified
- Sequential downloads simpler to test and debug
- Easier rollback logic with synchronous operations
- Performance goal (< 30 seconds) easily achievable with sync downloads

**Implementation Pattern**:
```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def download_template(url: str) -> str:
    with httpx.Client(timeout=10.0, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text
```

**Template Source URLs** (GitHub raw content):
```
https://raw.githubusercontent.com/{org}/{repo}/{branch}/path/to/template.md
```

**Cache Strategy**: No caching in v1
- Templates are small (< 10KB each)
- Caching adds complexity (cache invalidation, version tracking)
- Network dependency is explicit (user expectation: "downloads templates")
- Future enhancement: Cache in `~/.config/bpkit/cache/` with version tracking

**Alternatives Considered**:
- **Async httpx**: Rejected - overkill for 7 small files, adds complexity
- **requests library**: Rejected - httpx is modern, type-safe, matches Speckit dependencies
- **GitHub API**: Rejected - rate limiting concerns (60 req/hour unauthenticated), raw URLs simpler

---

## 2. Rollback Implementation

### Decision: Context manager with LIFO rollback tracking

**Rationale**:
- Ensures cleanup even if exceptions occur
- LIFO (last in, first out) order prevents orphaned directories
- Explicit tracking of what was created vs what existed before
- Atomic-like behavior: all-or-nothing installation

**Implementation Pattern**:
```python
from contextlib import contextmanager
from pathlib import Path
from typing import List, Tuple

class InstallationRollback:
    def __init__(self):
        self.created_files: List[Path] = []
        self.created_dirs: List[Path] = []

    def track_file(self, path: Path):
        if not path.exists():  # Only track if we're creating it
            self.created_files.append(path)

    def track_dir(self, path: Path):
        if not path.exists():  # Only track if we're creating it
            self.created_dirs.append(path)

    def rollback(self):
        # Delete files first (LIFO)
        for file_path in reversed(self.created_files):
            if file_path.exists():
                file_path.unlink()

        # Then delete directories (LIFO)
        for dir_path in reversed(self.created_dirs):
            if dir_path.exists() and not any(dir_path.iterdir()):
                dir_path.rmdir()  # Only remove if empty

@contextmanager
def atomic_installation():
    tracker = InstallationRollback()
    try:
        yield tracker
    except Exception as e:
        tracker.rollback()
        raise InstallationError(f"Installation failed: {e}. All changes rolled back.") from e
```

**Usage**:
```python
with atomic_installation() as tracker:
    # Create directory
    deck_dir = Path(".specify/deck")
    tracker.track_dir(deck_dir)
    deck_dir.mkdir(parents=True, exist_ok=False)

    # Download and write template
    template_path = Path(".specify/templates/pitch-deck-template.md")
    tracker.track_file(template_path)
    content = download_template(url)
    template_path.write_text(content)
    # If any step fails here, rollback() automatically called
```

**Safety Considerations**:
- Only delete paths explicitly tracked (never glob delete)
- Only delete directories if empty (prevents accidental data loss)
- Check `path.exists()` before tracking to distinguish created vs pre-existing

**Alternatives Considered**:
- **Transaction log file**: Rejected - overkill, adds file I/O overhead
- **Git-based rollback**: Rejected - Git is optional per requirements
- **Temp directory staging**: Rejected - doesn't handle directory creation rollback

---

## 3. CLI Prompting with Typer + Rich

### Decision: Use Typer.confirm() for Y/N prompts

**Rationale**:
- Built into Typer, no external dependencies
- Handles Ctrl+C gracefully (raises `typer.Abort`)
- Consistent UX with other Typer CLI tools
- Respects `--force` flag to skip prompts

**Implementation Pattern**:
```python
import typer
from rich.console import Console

console = Console()

def prompt_overwrite(force: bool = False) -> bool:
    """Prompt user to overwrite existing BP-Kit installation.

    Returns True if should proceed, False otherwise.
    Skips prompt if force=True.
    """
    if force:
        return True

    try:
        return typer.confirm(
            "BP-Kit already installed. Overwrite?",
            default=False  # Default to No (safe choice)
        )
    except typer.Abort:
        console.print("[yellow]Installation cancelled by user.[/yellow]")
        raise SystemExit(0)

def prompt_gitignore(force: bool = False) -> bool:
    """Prompt user to create .gitignore when no Git repo detected."""
    if force:
        return True  # Assume yes when --force

    try:
        return typer.confirm(
            "Git not detected. Create .gitignore for future use?",
            default=True  # Default to Yes (helpful for most users)
        )
    except typer.Abort:
        return False  # Continue without .gitignore if user cancels
```

**Prompt Defaults**:
- **Overwrite prompt**: Default to **No** (safe - prevents accidental data loss)
- **Git .gitignore prompt**: Default to **Yes** (helpful - users likely to init Git later)

**Ctrl+C Handling**:
- Overwrite prompt: Cancel entire installation (user explicitly aborts)
- Gitignore prompt: Continue without .gitignore (non-critical)

**--force Flag Behavior**:
- Skips all prompts
- Assumes "yes" to overwrite
- Assumes "yes" to .gitignore creation
- Used for CI/CD automation

**Alternatives Considered**:
- **Rich Prompt**: Rejected - Typer.confirm() is simpler, built-in
- **input() builtin**: Rejected - no Ctrl+C handling, no default value support
- **questionary library**: Rejected - additional dependency, overkill for simple Y/N

---

## 4. Speckit Detection Logic

### Decision: Check for `.specify/` directory existence only

**Rationale**:
- Clarification Q2 explicitly chose Option A: "`.specify/` directory exists"
- Simple, fast check (single `Path.exists()` call)
- Matches user expectation: "If I have `.specify/` folder, it's a Speckit project"
- Edge case handled: Empty `.specify/` treated as fresh install

**Implementation**:
```python
from pathlib import Path

def is_speckit_project(project_dir: Path = Path.cwd()) -> bool:
    """Detect if project already has Speckit installed.

    Returns True if `.specify/` directory exists.
    """
    return (project_dir / ".specify").exists()

def is_bpkit_installed(project_dir: Path = Path.cwd()) -> bool:
    """Detect if BP-Kit is already installed.

    Checks for presence of BP-Kit-specific files.
    """
    bpkit_markers = [
        ".specify/deck/",
        ".specify/templates/pitch-deck-template.md",
        ".claude/commands/bp.decompose.md",
    ]
    return any((project_dir / marker).exists() for marker in bpkit_markers)
```

**Why Not Check Specific Files?**:
- User may have partially configured Speckit (missing some files)
- `.specify/` folder is the canonical indicator
- Reduces false negatives (incorrectly thinking Speckit isn't installed)

**Edge Cases**:
- `.specify/` exists but empty → `is_speckit_project()` returns True, proceed with P1 flow (install in existing project)
- `.specify/` missing → `is_speckit_project()` returns False, proceed with P2 flow (bootstrap new project)

**Alternatives Considered**:
- **Check for `constitution.md`**: Rejected - not all Speckit projects have constitution (it's optional)
- **Check for Speckit templates**: Rejected - users might delete/customize templates
- **Multiple indicators (Option D from clarification)**: Rejected - user explicitly chose Option A

---

## 5. Template Placeholder Replacement

### Decision: Simple string replacement with `str.replace()`

**Rationale**:
- Templates are small (< 10KB), string replacement is fast
- Only one placeholder in v1: `[PROJECT_NAME]`
- No logic/conditionals in templates (just plain text substitution)
- Future-proof: Can upgrade to Jinja2 if placeholders become complex

**Implementation Pattern**:
```python
def replace_placeholders(content: str, project_name: str | None) -> str:
    """Replace template placeholders with actual values.

    Args:
        content: Template content with placeholders like [PROJECT_NAME]
        project_name: Project name to substitute, or None to leave unchanged

    Returns:
        Content with placeholders replaced
    """
    if project_name:
        content = content.replace("[PROJECT_NAME]", project_name)
    return content
```

**Usage**:
```python
# Download template
template_content = download_template(url)

# Replace placeholders if --project-name provided
if project_name:
    template_content = replace_placeholders(template_content, project_name)

# Write to file
template_path.write_text(template_content)
```

**Placeholder Conventions**:
- Use `[UPPERCASE_NAME]` format for easy visual scanning
- Current v1 placeholders: `[PROJECT_NAME]`
- Future placeholders (v2+): `[COMPANY_NAME]`, `[AUTHOR_NAME]`, `[DATE]`

**Alternatives Considered**:
- **Jinja2 templating**: Rejected - overkill for v1 (single placeholder), adds dependency
- **Regex replacement**: Rejected - `str.replace()` is simpler for exact matches
- **Template string (f-string)**: Rejected - requires eval() or complex parsing, security risk

---

## Implementation Priority

Based on research findings, implement in this order:

1. **Rollback mechanism** (foundational - needed by all other components)
2. **Template download** (core functionality)
3. **Speckit detection** (routing logic for P1 vs P2)
4. **Placeholder replacement** (simple feature, low risk)
5. **CLI prompting** (UX polish, can be added last)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Network failure during download | High | High | Retry logic (3 attempts), rollback on failure, clear error messages |
| Rollback leaves partial state | Low | High | LIFO tracking, only delete tracked paths, test extensively |
| False positive Speckit detection | Low | Medium | `.specify/` check is well-defined, edge cases documented |
| Placeholder collision | Very Low | Low | Use distinctive `[UPPERCASE]` format, document in templates |
| Ctrl+C during installation | Medium | Medium | Context manager ensures rollback, test abort scenarios |

---

## Performance Validation

**Target**: Complete `bpkit init` in < 30 seconds (SC-001)

**Estimated timings** (sequential downloads, 100ms network latency):
- Download 7 templates: 7 × (100ms latency + 50ms transfer) = ~1.05 seconds
- Create 4 directories: 4 × 1ms = 4ms
- Write 7 files: 7 × 5ms = 35ms
- Validation checks: 10ms
- User prompts (if any): 2-5 seconds
- **Total**: ~3-8 seconds (well under 30 second target)

**Bottleneck**: Network latency. Even with 500ms latency per request and 3 retries on failure, total time < 15 seconds.

---

## Conclusion

All research areas resolved. Ready to proceed to Phase 1 (data model and contracts).

**Key Technical Decisions**:
- Synchronous httpx with tenacity for retries
- Context manager rollback pattern
- Typer.confirm() for prompts
- `.specify/` directory existence for Speckit detection
- Simple string replacement for placeholders

**No Blockers**: All decisions align with constitution principles and functional requirements.
