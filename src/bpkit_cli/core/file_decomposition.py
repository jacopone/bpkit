"""File-based pitch deck decomposition."""

import shutil
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm

from ..models.decomposition import DecompositionMode, DecompositionResult, DecompositionWarning
from ..models.pitch_deck import SourceMode
from .constitution_generator import ConstitutionGenerator
from .sequoia_parser import SequoiaParser

console = Console()


class FileDecomposer:
    """Handles decomposition from existing markdown files."""

    def __init__(self, project_root: Path) -> None:
        """Initialize file decomposer.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.sequoia_parser = SequoiaParser()
        self.constitution_generator = ConstitutionGenerator(project_root)

    def decompose_from_file(
        self, file_path: Path, dry_run: bool = False, force: bool = False
    ) -> DecompositionResult:
        """Decompose pitch deck from markdown file.

        Args:
            file_path: Path to pitch deck markdown
            dry_run: Preview mode
            force: Overwrite without prompting

        Returns:
            DecompositionResult
        """
        # T021: Parse and validate Sequoia structure
        console.print(f"\n[cyan]Parsing pitch deck:[/cyan] {file_path}")
        pitch_deck = self.sequoia_parser.parse_pitch_deck(file_path, SourceMode.FROM_FILE)

        # Validate section content
        warnings_by_section = self.sequoia_parser.validate_all_sections(pitch_deck)
        if warnings_by_section:
            console.print("\n[yellow]Content warnings detected:[/yellow]")
            for section_id, warnings in warnings_by_section.items():
                for warning in warnings:
                    console.print(f"  [yellow]⚠[/yellow] {warning}")

        # T023: Copy file to canonical location (if different)
        canonical_path = self.project_root / ".specify" / "deck" / "pitch-deck.md"

        if not dry_run:
            copy_needed = file_path.resolve() != canonical_path.resolve()

            if copy_needed:
                if canonical_path.exists() and not force:
                    overwrite = Confirm.ask(
                        f"\nPitch deck exists at {canonical_path}. Overwrite?",
                        default=False,
                    )
                    if not overwrite:
                        console.print("[yellow]Operation cancelled.[/yellow]")
                        import typer

                        raise typer.Exit(2)

                # Copy file
                canonical_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, canonical_path)
                console.print(f"[green]✓[/green] Copied to canonical location: {canonical_path}")

                # Update pitch deck path
                pitch_deck.file_path = canonical_path

        # T022: Generate constitutions
        console.print("\n[cyan]Generating constitutions...[/cyan]")
        result = self.constitution_generator.generate_all_constitutions(
            pitch_deck, DecompositionMode.FROM_FILE, dry_run
        )

        # Add warnings from content validation
        for section_id, warnings in warnings_by_section.items():
            for warning_text in warnings:
                result.warnings.append(
                    DecompositionWarning(
                        code="CONTENT_WARNING",
                        message=warning_text,
                        section_id=section_id,
                        suggestion="Run 'bpkit clarify --section {section_id}' to resolve",
                    )
                )

        return result
