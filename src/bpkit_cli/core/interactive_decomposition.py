"""Interactive Q&A decomposition for pitch deck creation."""

from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ..models.decomposition import DecompositionMode, DecompositionResult
from ..models.pitch_deck import PitchDeck, PitchDeckSection, SourceMode
from ..models.sequoia_section import SequoiaSectionType
from .constitution_generator import ConstitutionGenerator

console = Console()


class InteractiveDecomposer:
    """Handles interactive Q&A pitch deck creation and decomposition."""

    def __init__(self, project_root: Path) -> None:
        """Initialize interactive decomposer.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.constitution_generator = ConstitutionGenerator(project_root)
        self.answers: dict[str, str] = {}

    def run_interactive_qa(self, dry_run: bool = False, force: bool = False) -> DecompositionResult:
        """Run interactive Q&A to create pitch deck and decompose.

        Args:
            dry_run: Preview mode
            force: Overwrite without prompting

        Returns:
            DecompositionResult
        """
        console.print("\n[bold cyan]Interactive Pitch Deck Creation[/bold cyan]\n")
        console.print(
            "Answer 10 questions to create your Sequoia-format pitch deck.\n"
            "Estimated time: 15 minutes\n"
        )

        # Check if pitch deck already exists
        pitch_deck_path = self.project_root / ".specify" / "deck" / "pitch-deck.md"
        if pitch_deck_path.exists() and not force:
            overwrite = Confirm.ask(
                f"\nPitch deck already exists at {pitch_deck_path}. Overwrite?",
                default=False,
            )
            if not overwrite:
                console.print("[yellow]Operation cancelled.[/yellow]")
                raise typer.Exit(2)

        # Collect answers for all 10 Sequoia sections
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task = progress.add_task("Collecting answers...", total=10)

            for section_type in SequoiaSectionType:
                self._ask_section_questions(section_type)
                progress.update(task, advance=1)

        # Display answers summary
        self._display_answers_summary()

        # Confirm before proceeding
        if not dry_run:
            proceed = Confirm.ask("\nProceed with decomposition?", default=True)
            if not proceed:
                console.print("[yellow]Operation cancelled.[/yellow]")
                raise typer.Exit(2)

        # Generate pitch deck markdown
        pitch_deck = self._generate_pitch_deck()

        # Save pitch deck (unless dry-run)
        if not dry_run:
            self._save_pitch_deck(pitch_deck)
            console.print(f"\n[green]✓[/green] Pitch deck saved: {pitch_deck_path}")

        # Generate constitutions
        result = self.constitution_generator.generate_all_constitutions(
            pitch_deck, DecompositionMode.INTERACTIVE, dry_run
        )

        return result

    def _ask_section_questions(self, section_type: SequoiaSectionType) -> None:
        """Ask questions for a specific section.

        Args:
            section_type: Sequoia section type
        """
        console.print(f"\n[bold]{section_type.get_title()}[/bold]")
        console.print("[dim]" + "─" * 60 + "[/dim]")

        prompts = section_type.get_prompts()

        # Display all prompts
        for idx, prompt in enumerate(prompts, start=1):
            console.print(f"  {idx}. {prompt}")

        console.print()

        # Collect answer with validation
        answer = self._get_validated_answer(section_type)
        self.answers[section_type.value] = answer

    def _get_validated_answer(self, section_type: SequoiaSectionType) -> str:
        """Get validated answer for section.

        Args:
            section_type: Section type

        Returns:
            Validated answer text
        """
        while True:
            answer = Prompt.ask("[cyan]Your answer[/cyan]")

            # Validate answer
            is_valid, message = self._validate_answer(answer, section_type)

            if is_valid:
                return answer

            # Show validation error and allow retry
            console.print(f"[yellow]⚠ {message}[/yellow]")
            retry = Confirm.ask("Try again?", default=True)
            if not retry:
                # Accept empty or minimal answer if user insists
                return answer

    def _validate_answer(self, answer: str, section_type: SequoiaSectionType) -> tuple[bool, str]:
        """Validate answer for section.

        Args:
            answer: User's answer
            section_type: Section type

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check minimum length
        if len(answer.strip()) < 5:
            return False, "Answer too short (minimum 5 characters)"

        # Section-specific validation
        if section_type == SequoiaSectionType.COMPANY_PURPOSE:
            # Company purpose should be a single sentence
            if len(answer.split()) > 30:
                return (
                    False,
                    "Company purpose should be concise (ideally one sentence, max 30 words)",
                )

        elif section_type in [
            SequoiaSectionType.MARKET_SIZE,
            SequoiaSectionType.FINANCIALS,
        ]:
            # Should contain numbers
            import re

            if not re.search(r"\d", answer):
                return (
                    False,
                    f"{section_type.get_title()} should include numbers/metrics",
                )

        return True, ""

    def _display_answers_summary(self) -> None:
        """Display summary of all collected answers."""
        console.print("\n[bold]Answers Summary[/bold]\n")

        table = Table(show_header=True, header_style="bold cyan", show_lines=True)
        table.add_column("Section", style="cyan", width=20)
        table.add_column("Answer", style="white", width=60)

        for section_type in SequoiaSectionType:
            answer = self.answers.get(section_type.value, "")
            # Truncate long answers for display
            display_answer = answer[:100] + "..." if len(answer) > 100 else answer
            table.add_row(section_type.get_title(), display_answer)

        console.print(table)

    def _generate_pitch_deck(self) -> PitchDeck:
        """Generate PitchDeck object from collected answers.

        Returns:
            PitchDeck instance
        """
        sections = []

        for idx, section_type in enumerate(SequoiaSectionType):
            answer = self.answers.get(section_type.value, "")

            section = PitchDeckSection(
                section_id=section_type.value,
                title=section_type.get_title(),
                content=answer,
                line_start=idx * 10,  # Approximate line numbers
                line_end=(idx + 1) * 10,
            )
            sections.append(section)

        pitch_deck_path = self.project_root / ".specify" / "deck" / "pitch-deck.md"

        pitch_deck = PitchDeck(
            file_path=pitch_deck_path,
            version="1.0.0",
            sections=sections,
            last_modified=datetime.now(),
            source_mode=SourceMode.INTERACTIVE,
        )

        return pitch_deck

    def _save_pitch_deck(self, pitch_deck: PitchDeck) -> None:
        """Save pitch deck to markdown file.

        Args:
            pitch_deck: PitchDeck instance
        """
        # Ensure directory exists
        pitch_deck.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate markdown content
        lines = [
            "---",
            f"version: {pitch_deck.version}",
            f"created: {datetime.now().strftime('%Y-%m-%d')}",
            f"updated: {datetime.now().strftime('%Y-%m-%d')}",
            "type: pitch-deck",
            f"source: {pitch_deck.source_mode.value}",
            "---",
            "",
            "# Pitch Deck",
            "",
        ]

        for section in pitch_deck.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            lines.append(section.content)
            lines.append("")

        content = "\n".join(lines)
        pitch_deck.file_path.write_text(content)
