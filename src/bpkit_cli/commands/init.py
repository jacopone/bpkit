"""BP-Kit init command implementation."""

from pathlib import Path
from typing import Optional

import typer
from pydantic import HttpUrl
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core import (
    InstallationError,
    TemplateDownloadError,
    atomic_installation,
    check_speckit_conflicts,
    detect_git,
    download_template,
    is_bpkit_installed,
    is_speckit_project,
    replace_placeholders,
)
from ..models import Template, TemplateType

console = Console()


# Template definitions from contracts/github-raw-api.yaml
TEMPLATE_BASE_URL = "https://raw.githubusercontent.com/jacopone/bpkit/003-implement-bp-decompose"

TEMPLATES = [
    Template(
        name="pitch-deck-template.md",
        source_url=HttpUrl(f"{TEMPLATE_BASE_URL}/.specify/templates/pitch-deck-template.md"),
        destination_path=Path(".specify/templates/pitch-deck-template.md"),
        type=TemplateType.MARKDOWN,
    ),
    Template(
        name="strategic-constitution-template.md",
        source_url=HttpUrl(
            f"{TEMPLATE_BASE_URL}/.specify/templates/strategic-constitution-template.md"
        ),
        destination_path=Path(".specify/templates/strategic-constitution-template.md"),
        type=TemplateType.MARKDOWN,
    ),
    Template(
        name="feature-constitution-template.md",
        source_url=HttpUrl(
            f"{TEMPLATE_BASE_URL}/.specify/templates/feature-constitution-template.md"
        ),
        destination_path=Path(".specify/templates/feature-constitution-template.md"),
        type=TemplateType.MARKDOWN,
    ),
    Template(
        name="bp.decompose.md",
        source_url=HttpUrl(f"{TEMPLATE_BASE_URL}/.claude/commands/bp.decompose.md"),
        destination_path=Path(".claude/commands/bp.decompose.md"),
        type=TemplateType.SLASH_COMMAND,
    ),
    Template(
        name="bp.sync.md",
        source_url=HttpUrl(f"{TEMPLATE_BASE_URL}/.claude/commands/bp.sync.md"),
        destination_path=Path(".claude/commands/bp.sync.md"),
        type=TemplateType.SLASH_COMMAND,
    ),
    Template(
        name="bp-common.sh",
        source_url=HttpUrl(f"{TEMPLATE_BASE_URL}/.specify/scripts/bp/bp-common.sh"),
        destination_path=Path(".specify/scripts/bp/bp-common.sh"),
        type=TemplateType.BASH_SCRIPT,
    ),
    Template(
        name="decompose-setup.sh",
        source_url=HttpUrl(f"{TEMPLATE_BASE_URL}/.specify/scripts/bp/decompose-setup.sh"),
        destination_path=Path(".specify/scripts/bp/decompose-setup.sh"),
        type=TemplateType.BASH_SCRIPT,
    ),
]


def prompt_gitignore(force: bool = False) -> bool:
    """Prompt user to create .gitignore when no Git repo detected.

    Args:
        force: If True, skip prompt and return True

    Returns:
        True if should create .gitignore, False otherwise
    """
    if force:
        return True  # Assume yes when --force

    try:
        return typer.confirm(
            "Git not detected. Create .gitignore for future use?",
            default=True,  # Default to Yes (helpful for most users)
        )
    except typer.Abort:
        # Non-critical prompt - continue without .gitignore if user cancels
        return False


def prompt_overwrite(force: bool = False) -> bool:
    """Prompt user to overwrite existing BP-Kit installation.

    Args:
        force: If True, skip prompt and return True

    Returns:
        True if should proceed with overwrite, False otherwise

    Raises:
        typer.Exit: If user cancels (Ctrl+C)
    """
    if force:
        return True

    try:
        return typer.confirm(
            "BP-Kit already installed. Overwrite?",
            default=False,  # Default to No (safe choice)
        )
    except typer.Abort:
        console.print("[yellow]Installation cancelled by user.[/yellow]")
        console.print("\nNo changes made.")
        raise typer.Exit(2)


def create_or_append_gitignore(project_dir: Path, tracker) -> None:
    """Create or append .gitignore with BP-Kit entry.

    Adds `.specify/deck/*.pdf` to .gitignore (pitch deck PDFs should not be committed).

    Args:
        project_dir: Project root directory
        tracker: InstallationRollback tracker
    """
    gitignore_path = project_dir / ".gitignore"
    bpkit_entry = ".specify/deck/*.pdf"

    if gitignore_path.exists():
        # Append if entry doesn't exist
        content = gitignore_path.read_text()
        if bpkit_entry not in content:
            # Add with comment
            content += f"\n# BP-Kit: Exclude pitch deck PDFs\n{bpkit_entry}\n"
            gitignore_path.write_text(content)
            console.print("[green]✓[/green] Updated .gitignore")
    else:
        # Create new .gitignore
        tracker.track_file(gitignore_path)
        content = f"# BP-Kit: Exclude pitch deck PDFs\n{bpkit_entry}\n"
        gitignore_path.write_text(content)
        console.print("[green]✓[/green] Created .gitignore")


def create_directories(project_dir: Path, tracker) -> None:
    """Create BP-Kit directory structure.

    Args:
        project_dir: Project root directory
        tracker: InstallationRollback tracker for rollback coordination

    Raises:
        InstallationError: If directory creation fails due to permissions or filesystem errors
    """
    directories = [
        ".specify/deck",
        ".specify/features",
        ".specify/changelog",
        ".specify/scripts/bp",
        ".specify/templates",
        ".claude/commands",
    ]

    for dir_path_str in directories:
        dir_path = project_dir / dir_path_str
        tracker.track_dir(dir_path)

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise InstallationError(
                f"Permission denied creating directory {dir_path}.\n"
                "Please check directory permissions or run with appropriate privileges."
            ) from e
        except OSError as e:
            raise InstallationError(
                f"Failed to create directory {dir_path}: {e}\n"
                "Please check disk space and file system permissions."
            ) from e

        console.print(f"[green]✓[/green] Created {dir_path_str}/")


def install_templates(project_dir: Path, tracker, project_name: Optional[str] = None) -> None:
    """Download and install BP-Kit templates.

    Args:
        project_dir: Project root directory
        tracker: InstallationRollback tracker
        project_name: Optional project name for placeholder replacement

    Raises:
        InstallationError: If template download fails with user-friendly message
    """
    total = len(TEMPLATES)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,  # Remove progress bar after completion
    ) as progress:
        for idx, template in enumerate(TEMPLATES, start=1):
            # Update progress
            task = progress.add_task(
                f"Downloading {template.name} ({idx}/{total})...",
                total=None
            )

            # Download template
            try:
                content = download_template(str(template.source_url))
            except TemplateDownloadError as e:
                # User-friendly error from download_template
                raise InstallationError(
                    f"Failed to download {template.name}:\n{e.reason}\n\n"
                    "Please check your internet connection and try again."
                ) from e
            except Exception as e:
                # Unexpected error - provide fallback message
                raise InstallationError(
                    f"Unexpected error downloading {template.name}: {e}\n"
                    "Please check your internet connection and try again."
                ) from e

            # Replace placeholders
            content = replace_placeholders(content, project_name)

            # Write to destination
            try:
                dest_path = project_dir / template.destination_path
                tracker.track_file(dest_path)
                dest_path.write_text(content)
            except PermissionError as e:
                raise InstallationError(
                    f"Permission denied writing to {dest_path}.\n"
                    "Please check directory permissions and try again."
                ) from e
            except OSError as e:
                raise InstallationError(
                    f"Failed to write {dest_path}: {e}\n"
                    "Please check disk space and file system permissions."
                ) from e

            progress.update(task, completed=True)

    # Display summary of what was installed
    console.print("\n[bold]Installed templates:[/bold]")
    for template in TEMPLATES:
        if template.type == TemplateType.MARKDOWN:
            console.print(f"  [green]✓[/green] {template.name}")
        elif template.type == TemplateType.SLASH_COMMAND:
            console.print(f"  [green]✓[/green] Slash command: /{template.name[:-3]}")
        elif template.type == TemplateType.BASH_SCRIPT:
            console.print(f"  [green]✓[/green] Bash utility: {template.name}")


def display_summary(project_name: Optional[str] = None) -> None:
    """Display installation summary and next steps.

    Args:
        project_name: Project name if provided
    """
    console.print("\\n[bold green]✨ BP-Kit successfully installed![/bold green]\\n")

    console.print("[bold]Next steps:[/bold]")
    console.print("  1. Create your pitch deck: .specify/deck/pitch-deck.md")
    console.print("  2. Run decomposition: /bp.decompose --interactive")
    console.print("  3. Verify installation: bpkit check")

    console.print("\\n[dim]Documentation: https://github.com/yourusername/bp-kit#readme[/dim]")


def run_init(project_name: Optional[str] = None, force: bool = False) -> None:
    """Run BP-Kit initialization.

    Main entry point for `bpkit init` command. Orchestrates:
    - Speckit detection
    - Conflict checking
    - Overwrite prompting
    - Directory creation
    - Template installation
    - Rollback on failure

    Args:
        project_name: Optional project name for template placeholders
        force: Skip all prompts if True

    Raises:
        typer.Exit: If user cancels or installation fails
    """
    project_dir = Path.cwd()

    # Detect existing installations
    has_speckit = is_speckit_project(project_dir)
    has_bpkit = is_bpkit_installed(project_dir)

    # Check for conflicts (informational only - BP-Kit won't overwrite Speckit files)
    conflicts = check_speckit_conflicts(project_dir)
    if conflicts and not force:
        console.print("[yellow]Note: Speckit files detected (will not be modified):[/yellow]")
        for conflict in conflicts:
            console.print(f"  [dim]{conflict}[/dim]")
        console.print()

    # If BP-Kit already installed, prompt for overwrite
    if has_bpkit:
        if not prompt_overwrite(force):
            console.print("\\nInstallation cancelled. No changes made.")
            console.print("\\n[dim]To force overwrite, run: bpkit init --force[/dim]")
            raise typer.Exit(2)

    # Begin atomic installation
    try:
        with atomic_installation() as tracker:
            # Create directory structure
            create_directories(project_dir, tracker)

            # Download and install templates
            install_templates(project_dir, tracker, project_name)

            # Create README placeholders
            readme_dirs = [
                ".specify/deck",
                ".specify/features",
                ".specify/changelog",
                ".specify/scripts/bp",
            ]
            for dir_path_str in readme_dirs:
                readme_path = project_dir / dir_path_str / "README.md"
                tracker.track_file(readme_path)
                readme_path.write_text(f"# {Path(dir_path_str).name.title()}\\n")

            # Handle .gitignore (US2 feature)
            has_git = detect_git(project_dir)
            if not has_git:
                # No Git detected - prompt user
                if prompt_gitignore(force):
                    create_or_append_gitignore(project_dir, tracker)
            else:
                # Git exists - always add/update .gitignore
                create_or_append_gitignore(project_dir, tracker)

            # Display success message
            if not has_speckit:
                # New project (US2) - show welcome message
                console.print("\\n[bold green]✨ BP-Kit successfully installed![/bold green]")
                console.print("\\n[bold]Welcome to BP-Kit![/bold]")
                console.print("\\nYou've created a new project with both Speckit and BP-Kit.")
                console.print("\\n[bold]Next steps:[/bold]")
                console.print("  1. Create your pitch deck: .specify/deck/pitch-deck.md")
                console.print("  2. Run decomposition: /bp.decompose --interactive")
                console.print("  3. Build features with Speckit workflow")
                console.print("\\n[dim]Documentation: https://github.com/yourusername/bp-kit#readme[/dim]")
            else:
                # Existing Speckit project (US1) - standard summary
                display_summary(project_name)

    except InstallationError as e:
        # Rollback already happened in atomic_installation context manager
        console.print(
            f"\\n[bold red]Error:[/bold red] {e}"
        )
        console.print("\\nRun 'bpkit init' to retry installation.")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\\n[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)
