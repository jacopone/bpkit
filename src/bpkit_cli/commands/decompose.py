"""BP-Kit decompose command - Transform pitch decks into constitutional specifications."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..models.decomposition import DecompositionMode, DecompositionResult

console = Console()


def decompose(
    interactive: bool = typer.Option(
        False,
        "--interactive",
        help="Interactive Q&A mode - create pitch deck from scratch",
    ),
    from_file: Optional[Path] = typer.Option(
        None,
        "--from-file",
        help="Path to existing markdown pitch deck file",
    ),
    from_pdf: Optional[Path] = typer.Option(
        None,
        "--from-pdf",
        help="Path to PDF pitch deck to extract and decompose",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview decomposition without writing files",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing constitutions without prompting",
    ),
) -> None:
    """
    Transform Sequoia pitch deck into constitutional specifications.

    Generates 4 strategic constitutions (company, product, market, business)
    and 5-10 feature constitutions with bidirectional traceability.

    \b
    Three modes available:
      1. --interactive: Create pitch deck via Q&A (15 min)
      2. --from-file:   Decompose existing markdown (< 2 min)
      3. --from-pdf:    Extract from PDF and decompose (< 2 min)

    \b
    Examples:
      bpkit decompose --interactive
      bpkit decompose --from-file ~/Documents/pitch-deck.md
      bpkit decompose --from-pdf ~/Downloads/pitch-deck.pdf --dry-run
    """
    # Validate mode selection
    mode_count = sum([interactive, from_file is not None, from_pdf is not None])

    if mode_count == 0:
        console.print("[bold red]Error:[/bold red] No mode specified")
        console.print("\nChoose one mode:")
        console.print("  --interactive      Create pitch deck via Q&A")
        console.print("  --from-file PATH   Decompose existing markdown")
        console.print("  --from-pdf PATH    Extract and decompose PDF")
        console.print("\nRun 'bpkit decompose --help' for more details")
        raise typer.Exit(1)

    if mode_count > 1:
        console.print("[bold red]Error:[/bold red] Multiple modes specified")
        console.print("\nUse only ONE mode at a time:")
        console.print("  --interactive")
        console.print("  --from-file")
        console.print("  --from-pdf")
        raise typer.Exit(1)

    # Determine mode
    if interactive:
        mode = DecompositionMode.INTERACTIVE
    elif from_file:
        mode = DecompositionMode.FROM_FILE
    else:
        mode = DecompositionMode.FROM_PDF

    # Display banner
    display_banner(mode, dry_run)

    # Execute decomposition based on mode
    try:
        if mode == DecompositionMode.INTERACTIVE:
            result = run_interactive_decomposition(dry_run, force)
        elif mode == DecompositionMode.FROM_FILE:
            result = run_file_decomposition(from_file, dry_run, force)  # type: ignore
        else:
            result = run_pdf_decomposition(from_pdf, dry_run, force)  # type: ignore

        # Display results
        display_results(result)

        # Exit with appropriate code
        if not result.is_success():
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Decomposition cancelled by user.[/yellow]")
        raise typer.Exit(2)
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


def display_banner(mode: DecompositionMode, dry_run: bool) -> None:
    """Display decomposition banner with mode information.

    Args:
        mode: Decomposition mode
        dry_run: Whether this is a dry-run
    """
    mode_text = {
        DecompositionMode.INTERACTIVE: "Interactive Q&A Mode",
        DecompositionMode.FROM_FILE: "Markdown File Decomposition",
        DecompositionMode.FROM_PDF: "PDF Extraction & Decomposition",
    }

    title = f"BP-Kit Decompose: {mode_text[mode]}"
    if dry_run:
        title += " [DRY RUN]"

    panel = Panel(
        f"[bold]Transform pitch deck → Constitutional specifications[/bold]\n\n"
        f"Mode: {mode_text[mode]}\n"
        f"{'Preview only (no files written)' if dry_run else 'Will create/update files'}",
        title=title,
        style="cyan",
    )
    console.print(panel)
    console.print()


def run_interactive_decomposition(dry_run: bool, force: bool) -> DecompositionResult:
    """Run interactive Q&A decomposition.

    Args:
        dry_run: Preview mode
        force: Overwrite without prompting

    Returns:
        DecompositionResult
    """
    from ..core.interactive_decomposition import InteractiveDecomposer

    decomposer = InteractiveDecomposer(Path.cwd())
    result = decomposer.run_interactive_qa(dry_run=dry_run, force=force)
    return result


def run_file_decomposition(
    file_path: Path, dry_run: bool, force: bool
) -> DecompositionResult:
    """Run decomposition from existing markdown file.

    Args:
        file_path: Path to pitch deck markdown
        dry_run: Preview mode
        force: Overwrite without prompting

    Returns:
        DecompositionResult

    Raises:
        typer.Exit: If file validation fails
    """
    from ..core.file_decomposition import FileDecomposer
    from ..core.sequoia_parser import SequoiaParseError

    # T020: File validation
    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
        raise typer.Exit(1)

    if not file_path.suffix == ".md":
        console.print(f"[bold red]Error:[/bold red] File must be markdown (.md): {file_path}")
        raise typer.Exit(1)

    # T021: Parse and validate
    try:
        decomposer = FileDecomposer(Path.cwd())
        result = decomposer.decompose_from_file(file_path, dry_run=dry_run, force=force)
        return result
    except SequoiaParseError as e:
        console.print(f"[bold red]Validation Error:[/bold red] {e}")
        console.print("\nExpected 10 Sequoia sections:")
        from ..models.sequoia_section import SequoiaSectionType

        for section_type in SequoiaSectionType:
            console.print(f"  - {section_type.get_title()}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


def run_pdf_decomposition(
    pdf_path: Path, dry_run: bool, force: bool
) -> DecompositionResult:
    """Run decomposition from PDF file.

    Args:
        pdf_path: Path to PDF pitch deck
        dry_run: Preview mode
        force: Overwrite without prompting

    Returns:
        DecompositionResult

    Raises:
        typer.Exit: If PDF validation fails
    """
    from ..core.pdf_decomposition import PDFDecomposer

    # File validation
    if not pdf_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {pdf_path}")
        raise typer.Exit(1)

    if not pdf_path.suffix.lower() == ".pdf":
        console.print(f"[bold red]Error:[/bold red] File must be PDF (.pdf): {pdf_path}")
        raise typer.Exit(1)

    try:
        decomposer = PDFDecomposer(Path.cwd())
        result = decomposer.decompose_from_pdf(pdf_path, dry_run=dry_run, force=force)
        return result
    except ImportError as e:
        console.print(f"[bold red]Dependency Error:[/bold red] {e}")
        console.print("\nInstall PDF support with: pip install pymupdf>=1.23.0")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)


def display_results(result: DecompositionResult) -> None:
    """Display decomposition results in formatted table.

    Args:
        result: Decomposition result to display
    """
    console.print("\n[bold]Decomposition Results[/bold]\n")

    # Create statistics table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Artifact Type", style="cyan")
    table.add_column("Count", justify="right", style="green")

    table.add_row("Strategic Constitutions", str(result.counts.strategic_constitutions))
    table.add_row("Feature Constitutions", str(result.counts.feature_constitutions))
    table.add_row("Total Principles", str(result.counts.total_principles))
    table.add_row("Traceability Links", str(result.counts.traceability_links))
    table.add_row("Entities Extracted", str(result.counts.entities_extracted))
    table.add_row("Success Criteria (Derived)", str(result.counts.success_criteria_derived))
    table.add_row(
        "Success Criteria (Placeholder)", str(result.counts.success_criteria_placeholder)
    )

    console.print(table)
    console.print()

    # Display warnings
    if result.has_warnings():
        console.print(f"[yellow]⚠ {len(result.warnings)} warning(s):[/yellow]")
        for warning in result.warnings:
            console.print(f"  [{warning.code}] {warning.message}")
            if warning.suggestion:
                console.print(f"    → Suggestion: {warning.suggestion}")
        console.print()

    # Display errors
    if not result.is_success():
        console.print(f"[bold red]✗ {len(result.errors)} error(s):[/bold red]")
        for error in result.errors:
            console.print(f"  [{error.code}] {error.message}")
        console.print()

    # Display summary message
    if result.is_success():
        if result.dry_run:
            console.print(
                "[bold green]✓ Decomposition preview complete[/bold green] "
                "(no files written)\n"
            )
            console.print("[dim]Remove --dry-run to create files[/dim]")
        else:
            console.print("[bold green]✓ Decomposition complete![/bold green]\n")
            console.print("[bold]Next steps:[/bold]")
            console.print("  1. Validate quality: bpkit analyze")
            console.print("  2. Review generated constitutions in .specify/")
            console.print(
                "  3. Implement features: /speckit.plan --constitution features/001-*.md"
            )
    else:
        console.print(
            "[bold red]✗ Decomposition failed[/bold red] - see errors above\n"
        )
        console.print("Fix errors and try again")
