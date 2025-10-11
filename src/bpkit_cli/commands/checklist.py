"""Checklist command for BP-Kit - generate quality validation checklists."""

from datetime import datetime
from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..models.checklist import Checklist, ChecklistItem
from ..models.constitution import Constitution, ConstitutionType

console = Console()


def checklist(
    report: bool = typer.Option(
        False,
        "--report",
        help="Show completion status of existing checklists",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing checklists",
    ),
) -> None:
    """Generate quality validation checklists for all constitutions.

    Creates structured checklists with validation criteria specific to
    strategic vs feature constitutions. Or reports completion status.

    Examples:
        bpkit checklist
        bpkit checklist --report
        bpkit checklist --force
    """
    # Check for constitutions
    memory_dir = Path(".specify/memory")
    features_dir = Path(".specify/features")

    if not memory_dir.exists() and not features_dir.exists():
        console.print("[red]Error:[/red] No constitutions found.", style="bold")
        console.print(
            "\nRun [cyan]/bp.decompose[/cyan] first to generate constitutions from pitch deck."
        )
        raise typer.Exit(code=1)

    checklists_dir = Path(".specify/checklists")

    # Report mode
    if report:
        _show_completion_report(checklists_dir)
        return

    # Generate mode
    console.print("[cyan]Scanning constitutions...[/cyan]")

    # Load constitutions
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

    strategic_count = sum(1 for c in constitutions if c.constitution_type == ConstitutionType.STRATEGIC)
    feature_count = sum(1 for c in constitutions if c.constitution_type == ConstitutionType.FEATURE)

    console.print(
        f"[green]✓[/green] Found {len(constitutions)} constitutions "
        f"({strategic_count} strategic, {feature_count} feature)\n"
    )

    # Create checklists directory
    checklists_dir.mkdir(parents=True, exist_ok=True)

    # Setup Jinja2 environment
    templates_dir = Path(__file__).parent.parent / "templates"
    env = Environment(loader=FileSystemLoader(str(templates_dir)))

    # Generate checklists
    console.print("[cyan]Generating checklists...[/cyan]")
    generated_count = 0
    skipped_count = 0

    for constitution in constitutions:
        checklist_file = checklists_dir / f"{constitution.name}.md"

        # Check if file exists
        if checklist_file.exists() and not force:
            skipped_count += 1
            console.print(
                f"[yellow]Skipping[/yellow] {constitution.name}.md (already exists)"
            )
            continue

        # Render template
        try:
            if constitution.constitution_type == ConstitutionType.STRATEGIC:
                template = env.get_template("strategic-checklist.j2")
                item_count = 10
            else:
                template = env.get_template("feature-checklist.j2")
                item_count = 15

            rendered = template.render(
                constitution_name=constitution.name,
                generated_date=datetime.now().strftime("%Y-%m-%d"),
            )

            checklist_file.write_text(rendered, encoding="utf-8")
            generated_count += 1
            console.print(
                f"[green]✓[/green] Generated {constitution.name}.md ({item_count} items)"
            )

        except TemplateNotFound as e:
            console.print(
                f"[red]Error:[/red] Template not found: {e}", style="bold"
            )
            continue
        except Exception as e:
            console.print(
                f"[red]Error:[/red] Failed to generate {constitution.name}.md: {e}",
                style="bold",
            )
            continue

    console.print()

    # Summary
    if generated_count > 0:
        console.print(
            Panel(
                f"[green bold]✅ Checklists generated for {generated_count} constitutions[/green bold]\n\n"
                f"Location: [cyan].specify/checklists/[/cyan]\n"
                f"Generated: {generated_count} new\n"
                f"Skipped: {skipped_count} existing\n\n"
                "Next steps:\n"
                "• Review checklists and check off items as you validate\n"
                "• Run [cyan]bpkit checklist --report[/cyan] to track completion progress\n"
                "• Once 100% complete, ready for [cyan]/speckit.implement[/cyan]",
                title="Checklist Generation Complete",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel(
                f"[yellow]No new checklists generated[/yellow]\n\n"
                f"All {len(constitutions)} constitutions already have checklists.\n\n"
                "Use [cyan]--force[/cyan] to overwrite existing checklists.\n"
                "Or run [cyan]--report[/cyan] to see completion status.",
                title="Checklist Generation",
                border_style="yellow",
            )
        )

    # Show hint about --report
    if generated_count > 0:
        console.print(
            "\n[dim]Tip: Run [cyan]bpkit checklist --report[/cyan] to see completion status[/dim]"
        )


def _show_completion_report(checklists_dir: Path) -> None:
    """Show completion report for all checklists.

    Args:
        checklists_dir: Path to .specify/checklists/
    """
    if not checklists_dir.exists() or not list(checklists_dir.glob("*.md")):
        console.print(
            "[yellow]No checklists found.[/yellow]\n\n"
            "Run [cyan]bpkit checklist[/cyan] first to generate checklists."
        )
        raise typer.Exit(code=0)

    console.print("[cyan]Analyzing checklist completion...[/cyan]\n")

    # Parse all checklists
    checklists: list[Checklist] = []
    for checklist_file in sorted(checklists_dir.glob("*.md")):
        try:
            checklist = Checklist.parse_from_file(checklist_file)
            checklists.append(checklist)
        except Exception as e:
            console.print(
                f"[yellow]Warning:[/yellow] Failed to parse {checklist_file.name}: {e}"
            )

    if not checklists:
        console.print("[red]Error:[/red] No valid checklists found.", style="bold")
        raise typer.Exit(code=1)

    # Create completion table
    table = Table(
        title="📊 Checklist Completion Report",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Constitution", style="white", width=30)
    table.add_column("Completion", justify="right", width=12)
    table.add_column("Remaining", justify="right", width=10)
    table.add_column("Status", justify="center", width=10)

    total_items = 0
    total_checked = 0

    for checklist in checklists:
        completion = checklist.calculate_completion()
        remaining = len([i for i in checklist.items if not i.is_checked])

        total_items += len(checklist.items)
        total_checked += len([i for i in checklist.items if i.is_checked])

        # Style based on completion
        if completion == 100.0:
            completion_str = f"[green]{completion:.0f}%[/green]"
            status = "[green]✅[/green]"
        elif completion >= 80.0:
            completion_str = f"[yellow]{completion:.0f}%[/yellow]"
            status = "[yellow]⚠️[/yellow]"
        else:
            completion_str = f"[red]{completion:.0f}%[/red]"
            status = "[red]❌[/red]"

        table.add_row(
            checklist.constitution_file.stem,
            completion_str,
            str(remaining),
            status,
        )

    console.print(table)

    # Overall summary
    overall_completion = (total_checked / total_items * 100.0) if total_items > 0 else 0.0
    overall_remaining = total_items - total_checked

    console.print()
    console.print(
        f"[bold]Overall:[/bold] {overall_completion:.0f}% complete "
        f"({overall_remaining} items remaining)"
    )

    # Next steps
    if overall_completion == 100.0:
        console.print(
            Panel(
                "[green bold]✅ All checklists 100% complete![/green bold]\n\n"
                "All constitutions have been validated.\n\n"
                "Ready for implementation:\n"
                "• Run [cyan]/speckit.plan[/cyan] for each feature\n"
                "• Or run [cyan]/speckit.implement[/cyan] to build features with AI agents",
                title="Ready for Implementation",
                border_style="green",
            )
        )
    else:
        incomplete = [c for c in checklists if c.calculate_completion() < 100.0]
        console.print(
            Panel(
                f"[yellow]Work in progress - {len(incomplete)} checklists incomplete[/yellow]\n\n"
                f"Complete remaining items to validate constitutional quality.\n\n"
                "Next steps:\n"
                "• Review and check off remaining validation items\n"
                "• Re-run [cyan]bpkit checklist --report[/cyan] to track progress\n"
                "• Once 100%, ready for [cyan]/speckit.implement[/cyan]",
                title="Checklist Status",
                border_style="yellow",
            )
        )
