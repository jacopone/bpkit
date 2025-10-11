"""BP-Kit check command implementation."""

from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.table import Table

from ..core import is_bpkit_installed, is_speckit_project

console = Console()


def check_directories(project_dir: Path) -> Tuple[bool, List[str]]:
    """Verify BP-Kit directory structure exists.

    Args:
        project_dir: Project root directory

    Returns:
        Tuple of (all_exist, missing_dirs)
    """
    required_dirs = [
        ".specify/deck",
        ".specify/features",
        ".specify/changelog",
        ".specify/scripts/bp",
        ".specify/templates",
        ".claude/commands",
    ]

    missing = []
    for dir_path_str in required_dirs:
        if not (project_dir / dir_path_str).exists():
            missing.append(dir_path_str)

    return len(missing) == 0, missing


def check_templates(project_dir: Path) -> Tuple[bool, List[str]]:
    """Verify BP-Kit templates are present.

    Args:
        project_dir: Project root directory

    Returns:
        Tuple of (all_exist, missing_templates)
    """
    required_templates = [
        ".specify/templates/pitch-deck-template.md",
        ".specify/templates/strategic-constitution-template.md",
        ".specify/templates/feature-constitution-template.md",
    ]

    missing = []
    for template_path_str in required_templates:
        if not (project_dir / template_path_str).exists():
            missing.append(template_path_str)

    return len(missing) == 0, missing


def check_slash_commands(project_dir: Path) -> Tuple[bool, List[str]]:
    """Verify BP-Kit slash commands are installed.

    Args:
        project_dir: Project root directory

    Returns:
        Tuple of (all_exist, missing_commands)
    """
    required_commands = [
        ".claude/commands/bp.decompose.md",
        ".claude/commands/bp.sync.md",
    ]

    missing = []
    for cmd_path_str in required_commands:
        if not (project_dir / cmd_path_str).exists():
            missing.append(cmd_path_str)

    return len(missing) == 0, missing


def check_bash_scripts(project_dir: Path) -> Tuple[bool, List[str]]:
    """Verify BP-Kit bash utilities are present.

    Args:
        project_dir: Project root directory

    Returns:
        Tuple of (all_exist, missing_scripts)
    """
    required_scripts = [
        ".specify/scripts/bp/bp-common.sh",
        ".specify/scripts/bp/decompose-setup.sh",
    ]

    missing = []
    for script_path_str in required_scripts:
        if not (project_dir / script_path_str).exists():
            missing.append(script_path_str)

    return len(missing) == 0, missing


def display_check_report(
    has_speckit: bool,
    has_bpkit: bool,
    dirs_ok: bool,
    missing_dirs: List[str],
    templates_ok: bool,
    missing_templates: List[str],
    commands_ok: bool,
    missing_commands: List[str],
    scripts_ok: bool,
    missing_scripts: List[str],
) -> None:
    """Display check results in a formatted table.

    Args:
        has_speckit: Whether Speckit is detected
        has_bpkit: Whether BP-Kit is installed
        dirs_ok: Whether all directories exist
        missing_dirs: List of missing directories
        templates_ok: Whether all templates exist
        missing_templates: List of missing templates
        commands_ok: Whether all slash commands exist
        missing_commands: List of missing commands
        scripts_ok: Whether all bash scripts exist
        missing_scripts: List of missing scripts
    """
    console.print("\n[bold cyan]BP-Kit Installation Check[/bold cyan]\n")

    # Create results table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Component", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Details")

    # Speckit detection
    table.add_row(
        "Speckit Project",
        "[green]✓[/green]" if has_speckit else "[yellow]✗[/yellow]",
        "Detected" if has_speckit else "Not found (BP-Kit can bootstrap new projects)"
    )

    # BP-Kit detection
    table.add_row(
        "BP-Kit Installed",
        "[green]✓[/green]" if has_bpkit else "[red]✗[/red]",
        "Installed" if has_bpkit else "Not installed - run 'bpkit init'"
    )

    # Directory structure
    table.add_row(
        "Directory Structure",
        "[green]✓[/green]" if dirs_ok else "[red]✗[/red]",
        "All present" if dirs_ok else f"Missing: {', '.join(missing_dirs)}"
    )

    # Templates
    table.add_row(
        "Templates",
        "[green]✓[/green]" if templates_ok else "[red]✗[/red]",
        "All present" if templates_ok else f"Missing: {', '.join(missing_templates)}"
    )

    # Slash commands
    table.add_row(
        "Slash Commands",
        "[green]✓[/green]" if commands_ok else "[red]✗[/red]",
        "All present" if commands_ok else f"Missing: {', '.join(missing_commands)}"
    )

    # Bash scripts
    table.add_row(
        "Bash Scripts",
        "[green]✓[/green]" if scripts_ok else "[red]✗[/red]",
        "All present" if scripts_ok else f"Missing: {', '.join(missing_scripts)}"
    )

    console.print(table)

    # Overall status
    all_ok = has_bpkit and dirs_ok and templates_ok and commands_ok and scripts_ok

    if all_ok:
        console.print("\n[bold green]✨ All systems ready![/bold green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  1. Create your pitch deck: .specify/deck/pitch-deck.md")
        console.print("  2. Run decomposition: /bp.decompose --interactive")
        console.print("  3. Build features with Speckit workflow")
    else:
        console.print("\n[bold yellow]⚠ Installation incomplete[/bold yellow]")
        if not has_bpkit:
            console.print("\nRun [bold]bpkit init[/bold] to install BP-Kit")
        else:
            console.print("\nRun [bold]bpkit init --force[/bold] to repair installation")


def run_check() -> None:
    """Run BP-Kit installation check.

    Main entry point for `bpkit check` command. Validates:
    - Speckit project detection
    - BP-Kit installation status
    - Directory structure
    - Template presence
    - Slash command installation
    - Bash script presence

    Displays formatted report with recommendations.
    """
    project_dir = Path.cwd()

    # Run all checks
    has_speckit = is_speckit_project(project_dir)
    has_bpkit = is_bpkit_installed(project_dir)

    dirs_ok, missing_dirs = check_directories(project_dir)
    templates_ok, missing_templates = check_templates(project_dir)
    commands_ok, missing_commands = check_slash_commands(project_dir)
    scripts_ok, missing_scripts = check_bash_scripts(project_dir)

    # Display report
    display_check_report(
        has_speckit=has_speckit,
        has_bpkit=has_bpkit,
        dirs_ok=dirs_ok,
        missing_dirs=missing_dirs,
        templates_ok=templates_ok,
        missing_templates=missing_templates,
        commands_ok=commands_ok,
        missing_commands=missing_commands,
        scripts_ok=scripts_ok,
        missing_scripts=missing_scripts,
    )
