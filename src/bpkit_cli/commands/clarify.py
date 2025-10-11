"""Clarify command for BP-Kit - identify and resolve pitch deck ambiguities."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from ..core.ambiguity_detector import AmbiguityDetector
from ..core.version_tracker import BumpType
from ..models.pitch_deck import PitchDeck

console = Console()


def clarify(
    section: Optional[str] = typer.Option(
        None,
        "--section",
        help="Focus clarification on specific pitch deck section ID",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show questions without updating pitch deck",
    ),
) -> None:
    """Analyze pitch deck for ambiguities and prompt user for clarifications.

    Identifies vague or incomplete sections in the pitch deck and asks targeted
    questions to resolve them. Updates the pitch deck in-place with answers.

    Examples:
        bpkit clarify
        bpkit clarify --section=business-model
        bpkit clarify --dry-run
    """
    # Find pitch deck file
    pitch_deck_path = Path(".specify/deck/pitch-deck.md")

    if not pitch_deck_path.exists():
        console.print(
            "[red]Error:[/red] Pitch deck not found at .specify/deck/pitch-deck.md",
            style="bold",
        )
        console.print("\nRun [cyan]bpkit init[/cyan] to create project structure.")
        raise typer.Exit(code=1)

    # Check if constitutions already exist (edge case handling)
    memory_dir = Path(".specify/memory")
    features_dir = Path(".specify/features")
    already_decomposed = (
        memory_dir.exists()
        and list(memory_dir.glob("*.md"))
        or features_dir.exists()
        and list(features_dir.glob("*.md"))
    )

    if already_decomposed:
        console.print(
            "[yellow]Warning:[/yellow] Pitch deck already decomposed into constitutions.",
            style="bold",
        )
        console.print(
            "Clarifications will update the pitch deck, but you'll need to re-run "
            "[cyan]/bp.decompose[/cyan] to regenerate constitutions.\n"
        )

    # Parse pitch deck
    console.print(f"[cyan]Parsing pitch deck:[/cyan] {pitch_deck_path}")
    try:
        deck = PitchDeck.parse(pitch_deck_path)
    except Exception as e:
        console.print(f"[red]Error parsing pitch deck:[/red] {e}", style="bold")
        raise typer.Exit(code=1)

    console.print(f"[green]✓[/green] Loaded pitch deck v{deck.version} with {len(deck.sections)} sections\n")

    # Detect vague sections
    detector = AmbiguityDetector()
    console.print("[cyan]Analyzing sections for ambiguities...[/cyan]")

    vague_sections = detector.detect_vague_sections(deck, target_section=section)

    if not vague_sections:
        console.print(
            Panel(
                "[green bold]✅ No clarifications needed - pitch deck is complete[/green bold]\n\n"
                "All sections have sufficient detail. Ready to run [cyan]/bp.decompose[/cyan].",
                title="Analysis Complete",
                border_style="green",
            )
        )
        raise typer.Exit(code=0)

    # Generate questions (max 5, prioritized)
    questions = [
        detector.generate_question(section, f"CLQ{i+1:03d}")
        for i, section in enumerate(vague_sections)
    ]
    prioritized_questions = detector.prioritize_questions(questions, max_questions=5)

    console.print(
        f"[yellow]Found {len(vague_sections)} sections needing clarification.[/yellow]"
    )
    console.print(
        f"[yellow]Asking {len(prioritized_questions)} highest-priority questions.[/yellow]\n"
    )

    if dry_run:
        console.print("[cyan]Dry run mode - questions will NOT update pitch deck.[/cyan]\n")

    # Ask questions interactively
    sections_updated = 0
    for question in prioritized_questions:
        answer = question.ask_interactively(console)

        if not dry_run:
            try:
                question.update_pitch_deck(deck)
                sections_updated += 1
                console.print(f"[green]✓[/green] Updated section '{question.section_id}'\n")
            except Exception as e:
                console.print(
                    f"[red]Error updating section '{question.section_id}':[/red] {e}\n"
                )

    # Save changes and bump version
    if not dry_run and sections_updated > 0:
        console.print("[cyan]Saving changes to pitch deck...[/cyan]")

        # Bump version (PATCH)
        old_version = deck.version
        new_version = deck.bump_version(BumpType.PATCH)

        try:
            deck.save()
            console.print(
                f"[green]✓[/green] Pitch deck updated: v{old_version} → v{new_version}\n"
            )
        except Exception as e:
            console.print(f"[red]Error saving pitch deck:[/red] {e}", style="bold")
            raise typer.Exit(code=1)

        # Log to changelog
        _log_clarification(sections_updated, old_version, new_version, section)

        # Show summary
        console.print(
            Panel(
                f"[green bold]✅ Pitch deck clarified - {sections_updated} sections updated[/green bold]\n\n"
                f"Version bumped: [cyan]v{old_version}[/cyan] → [cyan]v{new_version}[/cyan]\n\n"
                "Next steps:\n"
                "• Run [cyan]/bp.decompose[/cyan] to generate or regenerate constitutions\n"
                "• Run [cyan]/bp.analyze[/cyan] to validate constitutional consistency",
                title="Clarification Complete",
                border_style="green",
            )
        )
    elif dry_run:
        console.print(
            Panel(
                "[cyan]Dry run complete - no changes made to pitch deck.[/cyan]\n\n"
                f"Would have updated {sections_updated} sections and bumped version.\n\n"
                "Run without [yellow]--dry-run[/yellow] to apply changes.",
                title="Dry Run Complete",
                border_style="cyan",
            )
        )
    else:
        console.print(
            Panel(
                "[yellow]No sections were updated.[/yellow]\n\n"
                "All questions were answered but no changes applied.",
                title="Clarification Complete",
                border_style="yellow",
            )
        )


def _log_clarification(
    sections_updated: int, old_version: str, new_version: str, target_section: str | None
) -> None:
    """Log clarification operation to changelog.

    Args:
        sections_updated: Number of sections updated
        old_version: Old pitch deck version
        new_version: New pitch deck version
        target_section: Target section if focused, None if full deck
    """
    changelog_dir = Path(".specify/changelog")
    changelog_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d")
    scope = f"-{target_section}" if target_section else "-full"
    log_file = changelog_dir / f"{timestamp}-clarify{scope}.md"

    log_content = f"""# Clarification Log

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Operation**: /bp.clarify
**Scope**: {"Section: " + target_section if target_section else "Full pitch deck"}
**Sections Updated**: {sections_updated}
**Version**: {old_version} → {new_version}

## Changes

{sections_updated} sections clarified through interactive Q&A.

## Next Steps

- Run /bp.decompose to regenerate constitutions with clarifications
- Run /bp.analyze to validate constitutional consistency
"""

    log_file.write_text(log_content, encoding="utf-8")
