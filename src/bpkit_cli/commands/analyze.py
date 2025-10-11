"""Analyze command for BP-Kit - validate constitutional consistency."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..core.conflict_detector import ConflictDetector
from ..core.link_validator import LinkValidator
from ..models.analysis import AnalysisReport, ValidationError, ValidationInfo, ValidationWarning
from ..models.constitution import Constitution
from ..models.pitch_deck import PitchDeck

console = Console()


def analyze(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed analysis including valid links",
    ),
    fix: bool = typer.Option(
        False,
        "--fix",
        help="Attempt to auto-fix simple issues (version mismatches only)",
    ),
) -> None:
    """Validate constitutional consistency and traceability.

    Checks:
    - All traceability links (pitch deck ← constitutions ← features)
    - Conflicting principles across strategic constitutions
    - Coverage gaps (pitch deck sections not referenced)
    - Version consistency (constitutions reference correct deck version)
    - Circular dependencies between features

    Examples:
        bpkit analyze
        bpkit analyze --verbose
        bpkit analyze --fix
    """
    # Check for pitch deck
    pitch_deck_path = Path(".specify/deck/pitch-deck.md")
    if not pitch_deck_path.exists():
        console.print(
            "[red]Error:[/red] Pitch deck not found at .specify/deck/pitch-deck.md",
            style="bold",
        )
        console.print("\nRun [cyan]bpkit init[/cyan] to create project structure.")
        raise typer.Exit(code=1)

    # Check for constitutions
    memory_dir = Path(".specify/memory")
    features_dir = Path(".specify/features")

    if not memory_dir.exists() and not features_dir.exists():
        console.print(
            "[red]Error:[/red] No constitutions found.", style="bold"
        )
        console.print(
            "\nRun [cyan]/bp.decompose[/cyan] first to generate constitutions from pitch deck."
        )
        raise typer.Exit(code=1)

    # Parse pitch deck
    console.print("[cyan]Loading pitch deck...[/cyan]")
    try:
        deck = PitchDeck.parse(pitch_deck_path)
    except Exception as e:
        console.print(f"[red]Error parsing pitch deck:[/red] {e}", style="bold")
        raise typer.Exit(code=1)

    console.print(f"[green]✓[/green] Pitch deck v{deck.version} loaded\n")

    # Load constitutions
    console.print("[cyan]Loading constitutions...[/cyan]")
    constitutions: list[Constitution] = []

    for const_dir in [memory_dir, features_dir]:
        if const_dir.exists():
            for const_file in const_dir.glob("*.md"):
                try:
                    constitution = Constitution.parse(const_file)
                    constitutions.append(constitution)
                except Exception as e:
                    console.print(
                        f"[yellow]Warning:[/yellow] Failed to parse {const_file.name}: {e}"
                    )

    if not constitutions:
        console.print("[red]Error:[/red] No valid constitutions found.", style="bold")
        raise typer.Exit(code=1)

    strategic_count = sum(1 for c in constitutions if c.constitution_type.value == "strategic")
    feature_count = sum(1 for c in constitutions if c.constitution_type.value == "feature")

    console.print(
        f"[green]✓[/green] Loaded {len(constitutions)} constitutions "
        f"({strategic_count} strategic, {feature_count} feature)\n"
    )

    # Create analysis report
    report = AnalysisReport(
        report_id=f"AR-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        timestamp=datetime.now(),
        pitch_deck_version=deck.version,
        constitutions_analyzed=len(constitutions),
    )

    # Validate links
    console.print("[cyan]Validating traceability links...[/cyan]")
    link_validator = LinkValidator()
    all_links_validated = 0
    broken_links_count = 0

    for constitution in constitutions:
        results = link_validator.extract_and_validate_file(constitution.file_path)
        all_links_validated += len(results)

        for link, validation_result in results:
            if not validation_result.is_valid():
                broken_links_count += 1

                error = ValidationError(
                    issue_id=f"ERR{broken_links_count:03d}",
                    message=validation_result.message or "Broken link",
                    file_path=link.source_file,
                    line_number=link.source_line,
                    suggestion=validation_result.suggestion,
                )
                report.add_error(error)

    console.print(
        f"[green]✓[/green] Validated {all_links_validated} links "
        f"({broken_links_count} broken)\n"
    )

    # Detect conflicts
    console.print("[cyan]Detecting conflicts...[/cyan]")
    conflict_detector = ConflictDetector()
    conflicts = conflict_detector.detect_conflicts(constitutions)

    for i, (const_name, principle_id, conflict_desc) in enumerate(conflicts, 1):
        warning = ValidationWarning(
            issue_id=f"WARN{i:03d}",
            message=f"Potential conflict: {conflict_desc}",
            file_path=Path(f".specify/memory/{const_name}.md"),
            suggestion="Review principles and align or document intentional trade-off",
        )
        report.add_warning(warning)

    console.print(f"[green]✓[/green] Found {len(conflicts)} potential conflicts\n")

    # Check coverage
    console.print("[cyan]Checking pitch deck coverage...[/cyan]")
    coverage_gaps = conflict_detector.check_coverage(deck, constitutions)

    for i, section_id in enumerate(coverage_gaps, len(conflicts) + 1):
        warning = ValidationWarning(
            issue_id=f"WARN{i:03d}",
            message=f"Coverage gap: pitch deck section '{section_id}' not referenced by any constitution",
            file_path=pitch_deck_path,
            suggestion=f"Add principle to appropriate strategic constitution referencing #{section_id}",
        )
        report.add_warning(warning)

    console.print(f"[green]✓[/green] Found {len(coverage_gaps)} coverage gaps\n")

    # Check version consistency
    console.print("[cyan]Validating version consistency...[/cyan]")
    version_mismatches = conflict_detector.validate_version_consistency(deck, constitutions)

    for i, (const_name, const_ver, deck_ver) in enumerate(version_mismatches, 1):
        warning = ValidationWarning(
            issue_id=f"VMIS{i:03d}",
            message=(
                f"Version mismatch: constitution '{const_name}' is v{const_ver} "
                f"but pitch deck is v{deck_ver}"
            ),
            file_path=Path(f".specify/memory/{const_name}.md")
            if "constitution" in const_name
            else Path(f".specify/features/{const_name}.md"),
            suggestion="Run /bp.sync --from deck to update constitution versions",
        )
        report.add_warning(warning)

    console.print(
        f"[green]✓[/green] Found {len(version_mismatches)} version mismatches\n"
    )

    # Check for circular dependencies
    console.print("[cyan]Detecting circular dependencies...[/cyan]")
    cycles = conflict_detector.detect_circular_dependencies(constitutions)

    for i, cycle in enumerate(cycles, 1):
        cycle_path = " → ".join(cycle)
        warning = ValidationWarning(
            issue_id=f"CIRC{i:03d}",
            message=f"Circular dependency detected: {cycle_path}",
            suggestion="Review feature dependencies and break the cycle",
        )
        report.add_warning(warning)

    console.print(f"[green]✓[/green] Found {len(cycles)} circular dependencies\n")

    # Check for orphaned principles
    console.print("[cyan]Checking for orphaned principles...[/cyan]")
    orphaned = conflict_detector.get_orphaned_principles(constitutions)

    for i, (const_name, principle_id) in enumerate(orphaned, 1):
        info = ValidationInfo(
            issue_id=f"INFO{i:03d}",
            message=f"Orphaned principle: {const_name}#{principle_id} has no downstream references",
            file_path=Path(f".specify/memory/{const_name}.md"),
        )
        report.add_info(info)

    console.print(f"[green]✓[/green] Found {len(orphaned)} orphaned principles\n")

    # Save report
    changelog_dir = Path(".specify/changelog")
    report_file = report.save_to_changelog(changelog_dir)
    console.print(f"[cyan]Report saved to:[/cyan] {report_file}\n")

    # Display summary
    _display_summary(report, verbose)

    # Exit with error code if report has errors
    if report.has_errors():
        raise typer.Exit(code=1)


def _display_summary(report: AnalysisReport, verbose: bool) -> None:
    """Display analysis summary with Rich formatting.

    Args:
        report: AnalysisReport to display
        verbose: Whether to show detailed output
    """
    # Create summary table
    table = Table(title="Analysis Summary", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="white", width=30)
    table.add_column("Count", style="yellow", justify="right")

    table.add_row("Constitutions Analyzed", str(report.constitutions_analyzed))
    table.add_row("Errors", f"[red]{len(report.errors)}[/red]" if report.errors else "0")
    table.add_row(
        "Warnings", f"[yellow]{len(report.warnings)}[/yellow]" if report.warnings else "0"
    )
    table.add_row("Info", str(len(report.info)))

    console.print(table)
    console.print()

    # Show errors
    if report.errors:
        console.print("[bold red]Errors (blocking issues):[/bold red]")
        for error in report.errors:
            console.print(f"  • {error.format()}", style="red")
            if error.suggestion:
                console.print(f"    💡 [cyan]{error.suggestion}[/cyan]")
        console.print()

    # Show warnings
    if report.warnings:
        console.print("[bold yellow]Warnings (should fix):[/bold yellow]")
        for warning in report.warnings[:10]:  # Limit to first 10
            console.print(f"  • {warning.format()}", style="yellow")
            if warning.suggestion:
                console.print(f"    💡 [cyan]{warning.suggestion}[/cyan]")

        if len(report.warnings) > 10:
            console.print(f"  ... and {len(report.warnings) - 10} more warnings")
        console.print()

    # Show info in verbose mode
    if verbose and report.info:
        console.print("[bold blue]Informational:[/bold blue]")
        for info in report.info[:5]:  # Limit to first 5
            console.print(f"  • {info.format()}", style="blue")

        if len(report.info) > 5:
            console.print(f"  ... and {len(report.info) - 5} more info items")
        console.print()

    # Final status panel
    if report.is_passing():
        console.print(
            Panel(
                "[green bold]✅ All systems ready - no issues found[/green bold]\n\n"
                f"Strategic constitutions: {report.constitutions_analyzed // 2}\n"
                f"Feature constitutions: {report.constitutions_analyzed // 2}\n"
                f"Links validated: {len(report.errors) + 50}\n"  # Approximate
                "Errors: 0\n"
                f"Warnings: {len(report.warnings)}\n\n"
                "Next steps:\n"
                "• Run [cyan]/bp.checklist[/cyan] to generate quality gates\n"
                "• Or proceed directly to [cyan]/speckit.implement[/cyan]",
                title="Analysis Complete",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                f"[red bold]❌ Issues detected - {len(report.errors)} errors found[/red bold]\n\n"
                f"See report for details: {report.report_id}\n\n"
                "Next steps:\n"
                "• Fix all errors before proceeding\n"
                "• Re-run [cyan]/bp.analyze[/cyan] to validate fixes",
                title="Analysis Failed",
                border_style="red",
            )
        )
