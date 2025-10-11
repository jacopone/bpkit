"""
BP-Kit CLI - Transform business plans into executable MVP specifications

This tool decomposes Sequoia-format pitch decks into constitutional principles
that AI agents can implement, with bidirectional traceability.
"""

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

__version__ = "0.1.0"

console = Console()


class BannerGroup(typer.core.TyperGroup):
    """Custom Typer group that displays banner before help text"""

    def format_help(self, ctx: typer.Context, formatter: typer.core.HelpFormatter) -> None:
        banner = """
╔══════════════════════════════════════════════════════════════╗
║              BP-Kit: Business Plan to Constitution           ║
║           Transform pitch decks into executable MVPs         ║
║                                                               ║
║  Companion tool to Speckit for business-driven development   ║
╚══════════════════════════════════════════════════════════════╝
"""
        console.print(banner, style="bold cyan")
        super().format_help(ctx, formatter)


app = typer.Typer(
    cls=BannerGroup,
    name="bpkit",
    help="Transform business plans into executable MVP specifications for AI agents",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def init(
    project_name: Optional[str] = typer.Argument(
        None, help="Name of the project to initialize BP-Kit for"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing BP-Kit setup"),
) -> None:
    """
    Initialize BP-Kit templates in a Speckit project.

    This command sets up the BP-Kit directory structure and templates
    in an existing Speckit project, enabling business plan decomposition.
    """
    from .commands.init import run_init

    run_init(project_name, force)


@app.command()
def check() -> None:
    """
    Verify BP-Kit installation and dependencies.

    Checks that all required tools and templates are properly installed.
    """
    from .commands.check import run_check

    try:
        run_check()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def clarify(
    section: Optional[str] = typer.Option(
        None, "--section", help="Focus clarification on specific pitch deck section ID"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show questions without updating pitch deck"
    ),
) -> None:
    """
    Analyze pitch deck for ambiguities and prompt for clarifications.

    Identifies vague or incomplete sections and asks targeted questions
    to resolve them. Updates pitch deck in-place with answers.
    """
    from .commands.clarify import clarify as run_clarify

    try:
        run_clarify(section, dry_run)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def analyze(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed analysis including valid links"
    ),
    fix: bool = typer.Option(
        False, "--fix", help="Attempt to auto-fix simple issues (version mismatches only)"
    ),
) -> None:
    """
    Validate constitutional consistency and traceability.

    Checks all links, detects conflicts, validates versions, and reports
    coverage gaps. Generates detailed analysis report.
    """
    from .commands.analyze import analyze as run_analyze

    try:
        run_analyze(verbose, fix)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def checklist(
    report: bool = typer.Option(
        False, "--report", help="Show completion status of existing checklists"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite existing checklists"
    ),
) -> None:
    """
    Generate quality validation checklists for all constitutions.

    Creates structured checklists with validation criteria specific to
    strategic vs feature constitutions. Or reports completion status.
    """
    from .commands.checklist import checklist as run_checklist

    try:
        run_checklist(report, force)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def decompose(
    interactive: bool = typer.Option(
        False, "--interactive", help="Interactive Q&A mode - create pitch deck from scratch"
    ),
    from_file: Optional[str] = typer.Option(
        None, "--from-file", help="Path to existing markdown pitch deck file"
    ),
    from_pdf: Optional[str] = typer.Option(
        None, "--from-pdf", help="Path to PDF pitch deck to extract and decompose"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview decomposition without writing files"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite existing constitutions without prompting"
    ),
) -> None:
    """
    Transform Sequoia pitch deck into constitutional specifications.

    Generates 4 strategic constitutions (company, product, market, business)
    and 5-10 feature constitutions with bidirectional traceability.
    """
    from pathlib import Path

    from .commands.decompose import decompose as run_decompose

    # Convert string paths to Path objects
    from_file_path = Path(from_file) if from_file else None
    from_pdf_path = Path(from_pdf) if from_pdf else None

    try:
        run_decompose(interactive, from_file_path, from_pdf_path, dry_run, force)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@app.command()
def version() -> None:
    """Show BP-Kit version information"""
    console.print(f"[bold cyan]BP-Kit CLI[/bold cyan] version [bold]{__version__}[/bold]")
    console.print("\nCompanion tool to Speckit for business-driven development")
    console.print("Homepage: https://github.com/yourusername/bp-kit")


def main() -> None:
    """Main entry point for the BP-Kit CLI"""
    app()


if __name__ == "__main__":
    main()
