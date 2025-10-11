"""PDF-based pitch deck decomposition with extraction and validation."""

from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm

from ..models.decomposition import DecompositionMode, DecompositionResult, DecompositionWarning
from ..models.pitch_deck import SourceMode
from .constitution_generator import ConstitutionGenerator
from .pdf_extractor import PDFExtractor
from .sequoia_parser import SequoiaParser, SequoiaParseError

console = Console()


class PDFDecomposer:
    """Handles decomposition from PDF files."""

    def __init__(self, project_root: Path) -> None:
        """Initialize PDF decomposer.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.pdf_extractor = PDFExtractor()
        self.sequoia_parser = SequoiaParser()
        self.constitution_generator = ConstitutionGenerator(project_root)

    def decompose_from_pdf(
        self, pdf_path: Path, dry_run: bool = False, force: bool = False
    ) -> DecompositionResult:
        """Decompose pitch deck from PDF file.

        Args:
            pdf_path: Path to PDF file
            dry_run: Preview mode
            force: Overwrite without prompting

        Returns:
            DecompositionResult
        """
        # T024: Extract PDF content
        console.print(f"\n[cyan]Extracting text from PDF:[/cyan] {pdf_path}")
        extraction_result = self.pdf_extractor.extract_pitch_deck(pdf_path)

        console.print(f"[green]✓[/green] Extracted {len(extraction_result.sections)} sections")
        console.print(f"[dim]Confidence: {extraction_result.confidence:.0%}[/dim]")

        # Display extraction warnings
        if extraction_result.warnings:
            console.print("\n[yellow]Extraction warnings:[/yellow]")
            for warning in extraction_result.warnings:
                console.print(f"  [yellow]⚠[/yellow] {warning}")

        # T025: Convert to markdown
        console.print("\n[cyan]Converting to markdown...[/cyan]")
        markdown_content = self.pdf_extractor.convert_to_markdown(extraction_result)

        # T026: Save markdown pitch deck
        pitch_deck_path = self.project_root / ".specify" / "deck" / "pitch-deck.md"

        if not dry_run:
            if pitch_deck_path.exists() and not force:
                overwrite = Confirm.ask(
                    f"\nPitch deck exists at {pitch_deck_path}. Overwrite?",
                    default=False,
                )
                if not overwrite:
                    console.print("[yellow]Operation cancelled.[/yellow]")
                    import typer

                    raise typer.Exit(2)

            pitch_deck_path.parent.mkdir(parents=True, exist_ok=True)
            pitch_deck_path.write_text(markdown_content)
            console.print(f"[green]✓[/green] Saved markdown: {pitch_deck_path}")

        # T027: Parse and validate
        try:
            pitch_deck = self.sequoia_parser.parse_pitch_deck(
                pitch_deck_path, SourceMode.FROM_PDF
            )
        except SequoiaParseError as e:
            # PDF extraction may have failed to detect all sections
            console.print(f"\n[yellow]Validation warning:[/yellow] {e}")
            console.print("\n[dim]Manual review of extracted pitch deck recommended.[/dim]")
            console.print(f"[dim]Edit: {pitch_deck_path}[/dim]")

            # Ask if user wants to continue with partial extraction
            if not force and not dry_run:
                proceed = Confirm.ask("\nContinue with partial extraction?", default=False)
                if not proceed:
                    import typer

                    raise typer.Exit(2)

            # Re-parse with error handling (may fail)
            from ..models.pitch_deck import PitchDeck

            pitch_deck = PitchDeck.parse(pitch_deck_path)
            pitch_deck.source_mode = SourceMode.FROM_PDF

        # Generate constitutions
        console.print("\n[cyan]Generating constitutions...[/cyan]")
        result = self.constitution_generator.generate_all_constitutions(
            pitch_deck, DecompositionMode.FROM_PDF, dry_run
        )

        # Add PDF extraction warnings to result
        for warning_text in extraction_result.warnings:
            result.warnings.append(
                DecompositionWarning(
                    code="PDF_EXTRACTION_WARNING",
                    message=warning_text,
                    suggestion="Review extracted pitch deck manually",
                )
            )

        # Add low confidence warning
        if extraction_result.confidence < 0.85:
            result.warnings.append(
                DecompositionWarning(
                    code="LOW_EXTRACTION_CONFIDENCE",
                    message=f"PDF extraction confidence {extraction_result.confidence:.0%} (below 85% threshold)",
                    suggestion=f"Review and edit {pitch_deck_path}, then re-run with --from-file",
                )
            )

        return result
