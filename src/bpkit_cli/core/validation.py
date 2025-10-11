"""Validation utilities for BP-Kit installation."""

from pathlib import Path
from typing import List


def is_speckit_project(project_dir: Path = Path.cwd()) -> bool:
    """Detect if project has Speckit installed.

    Per clarification Q2: Checks for `.specify/` directory existence.

    Args:
        project_dir: Project root directory (default: current working directory)

    Returns:
        True if `.specify/` directory exists

    Example:
        >>> is_speckit_project(Path("/path/to/speckit-project"))
        True
        >>> is_speckit_project(Path("/path/to/empty-dir"))
        False
    """
    return (project_dir / ".specify").exists()


def is_bpkit_installed(project_dir: Path = Path.cwd()) -> bool:
    """Detect if BP-Kit is already installed.

    Checks for presence of BP-Kit-specific markers:
    - .specify/deck/ directory
    - .specify/templates/pitch-deck-template.md
    - .claude/commands/bp.decompose.md

    Args:
        project_dir: Project root directory (default: current working directory)

    Returns:
        True if any BP-Kit marker files/directories exist

    Example:
        >>> is_bpkit_installed(Path("/path/to/bpkit-project"))
        True
        >>> is_bpkit_installed(Path("/path/to/speckit-only-project"))
        False
    """
    bpkit_markers = [
        project_dir / ".specify" / "deck",
        project_dir / ".specify" / "templates" / "pitch-deck-template.md",
        project_dir / ".claude" / "commands" / "bp.decompose.md",
    ]
    return any(marker.exists() for marker in bpkit_markers)


def check_speckit_conflicts(project_dir: Path = Path.cwd()) -> List[str]:
    """Validate that BP-Kit installation won't conflict with Speckit files.

    Per FR-006: Ensures no overwrites of:
    - /speckit.* slash commands
    - Speckit templates (spec-template.md, plan-template.md, tasks-template.md)

    Args:
        project_dir: Project root directory (default: current working directory)

    Returns:
        List of conflict descriptions (empty if no conflicts)

    Example:
        >>> conflicts = check_speckit_conflicts(Path("/path/to/project"))
        >>> if not conflicts:
        ...     print("No conflicts - safe to proceed")
    """
    conflicts = []

    # Check for Speckit slash commands that BP-Kit might overwrite
    speckit_commands = [
        ".claude/commands/speckit.constitution.md",
        ".claude/commands/speckit.specify.md",
        ".claude/commands/speckit.plan.md",
        ".claude/commands/speckit.tasks.md",
        ".claude/commands/speckit.implement.md",
    ]

    for cmd_path in speckit_commands:
        full_path = project_dir / cmd_path
        if full_path.exists():
            # BP-Kit should never overwrite these
            conflicts.append(
                f"Speckit command exists: {cmd_path} (BP-Kit will not modify)"
            )

    # Check for Speckit templates
    speckit_templates = [
        ".specify/templates/spec-template.md",
        ".specify/templates/plan-template.md",
        ".specify/templates/tasks-template.md",
    ]

    for template_path in speckit_templates:
        full_path = project_dir / template_path
        if full_path.exists():
            # BP-Kit should never overwrite these
            conflicts.append(
                f"Speckit template exists: {template_path} (BP-Kit will not modify)"
            )

    # Note: BP-Kit conflicts are informational, not blocking
    # BP-Kit templates have different names (pitch-deck-template.md, etc.)
    # so they won't actually overwrite Speckit files

    return conflicts


def detect_git(project_dir: Path = Path.cwd()) -> bool:
    """Detect if Git repository exists in project.

    Args:
        project_dir: Project root directory (default: current working directory)

    Returns:
        True if .git/ directory detected

    Example:
        >>> detect_git(Path("/path/to/git-repo"))
        True
        >>> detect_git(Path("/path/to/no-git"))
        False
    """
    return (project_dir / ".git").exists()
