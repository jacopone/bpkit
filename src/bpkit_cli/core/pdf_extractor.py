"""PDF pitch deck extraction using PyMuPDF with font size heuristics."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import pymupdf  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


@dataclass
class PDFSection:
    """Represents an extracted section from PDF."""

    title: str
    """Section title"""

    content: str
    """Section content"""

    page_number: int
    """Page where section starts"""

    confidence: float
    """Extraction confidence (0.0-1.0)"""


@dataclass
class PDFExtractionResult:
    """Result of PDF extraction operation."""

    sections: list[PDFSection]
    """Extracted sections"""

    total_pages: int
    """Total pages in PDF"""

    confidence: float
    """Overall extraction confidence"""

    warnings: list[str]
    """Extraction warnings"""


class PDFExtractor:
    """Extracts pitch deck content from PDF using font size detection."""

    # Font size thresholds (typical pitch deck formatting)
    TITLE_FONT_SIZE_MIN = 18  # Minimum font size for section headings
    BODY_FONT_SIZE_MAX = 14  # Maximum font size for body text

    def __init__(self) -> None:
        """Initialize PDF extractor.

        Raises:
            ImportError: If PyMuPDF is not installed
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF (pymupdf) is required for PDF extraction.\n"
                "Install with: pip install pymupdf>=1.23.0"
            )

    def extract_pitch_deck(self, pdf_path: Path) -> PDFExtractionResult:
        """Extract pitch deck sections from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            PDFExtractionResult with sections and metadata

        Raises:
            FileNotFoundError: If PDF file does not exist
            ValueError: If PDF cannot be opened or parsed

        Example:
            >>> extractor = PDFExtractor()
            >>> result = extractor.extract_pitch_deck(Path("pitch-deck.pdf"))
            >>> result.confidence > 0.85
            True
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            doc = pymupdf.open(pdf_path)
        except Exception as e:
            raise ValueError(f"Failed to open PDF: {e}") from e

        sections = []
        warnings = []
        total_pages = len(doc)

        current_section_title = None
        current_section_content = []
        current_section_page = 1

        for page_num in range(total_pages):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            font_size = span.get("size", 0)

                            if not text:
                                continue

                            # Detect section heading by font size
                            if font_size >= self.TITLE_FONT_SIZE_MIN:
                                # Save previous section if exists
                                if current_section_title:
                                    section = PDFSection(
                                        title=current_section_title,
                                        content="\n".join(current_section_content),
                                        page_number=current_section_page,
                                        confidence=0.85,
                                    )
                                    sections.append(section)

                                # Start new section
                                current_section_title = text
                                current_section_content = []
                                current_section_page = page_num + 1

                            # Body text
                            elif font_size <= self.BODY_FONT_SIZE_MAX:
                                if current_section_title:
                                    current_section_content.append(text)

        # Save final section
        if current_section_title:
            section = PDFSection(
                title=current_section_title,
                content="\n".join(current_section_content),
                page_number=current_section_page,
                confidence=0.85,
            )
            sections.append(section)

        doc.close()

        # Calculate overall confidence
        overall_confidence = self._calculate_confidence(sections, total_pages)

        # Generate warnings
        if len(sections) < 10:
            warnings.append(
                f"Only {len(sections)} sections detected (expected 10 Sequoia sections)"
            )

        if overall_confidence < 0.85:
            warnings.append(
                f"Extraction confidence low ({overall_confidence:.0%}). Manual review recommended."
            )

        return PDFExtractionResult(
            sections=sections,
            total_pages=total_pages,
            confidence=overall_confidence,
            warnings=warnings,
        )

    def _calculate_confidence(self, sections: list[PDFSection], total_pages: int) -> float:
        """Calculate overall extraction confidence.

        Args:
            sections: Extracted sections
            total_pages: Total pages in PDF

        Returns:
            Confidence score (0.0-1.0)
        """
        # Base confidence
        confidence = 0.50

        # Increase confidence based on section count
        if len(sections) >= 10:
            confidence += 0.30  # Expected 10 Sequoia sections
        elif len(sections) >= 5:
            confidence += 0.15

        # Increase confidence if sections have content
        sections_with_content = sum(1 for s in sections if len(s.content) > 20)
        if sections_with_content >= 8:
            confidence += 0.20
        elif sections_with_content >= 5:
            confidence += 0.10

        return min(confidence, 1.0)

    def convert_to_markdown(self, result: PDFExtractionResult) -> str:
        """Convert extracted sections to markdown format.

        Args:
            result: PDF extraction result

        Returns:
            Markdown-formatted pitch deck

        Example:
            >>> extractor = PDFExtractor()
            >>> result = extractor.extract_pitch_deck(Path("pitch-deck.pdf"))
            >>> markdown = extractor.convert_to_markdown(result)
            >>> "##" in markdown
            True
        """
        lines = [
            "---",
            "version: 1.0.0",
            "created: [NEEDS REVIEW]",
            "updated: [NEEDS REVIEW]",
            "type: pitch-deck",
            "source: PDF extraction",
            "---",
            "",
            "# Pitch Deck",
            "",
        ]

        for section in result.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            lines.append(section.content)
            lines.append("")

        # Add warnings as comments if low confidence
        if result.warnings:
            lines.append("<!-- EXTRACTION WARNINGS -->")
            for warning in result.warnings:
                lines.append(f"<!-- {warning} -->")

        return "\n".join(lines)
