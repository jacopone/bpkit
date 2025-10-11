"""Sequoia Capital pitch deck parser and validator."""

from pathlib import Path

from ..models.pitch_deck import PitchDeck, PitchDeckSection, SourceMode
from ..models.sequoia_section import SequoiaSectionType
from .markdown_parser import MarkdownParser


class SequoiaParseError(Exception):
    """Raised when pitch deck fails Sequoia validation."""

    pass


class SequoiaParser:
    """Parses and validates Sequoia Capital pitch deck structure."""

    def __init__(self) -> None:
        """Initialize Sequoia parser with markdown parser."""
        self._markdown_parser = MarkdownParser()

    def parse_pitch_deck(
        self, file_path: Path, source_mode: SourceMode = SourceMode.FROM_FILE
    ) -> PitchDeck:
        """Parse pitch deck and validate Sequoia structure.

        Args:
            file_path: Path to pitch deck markdown file
            source_mode: How this pitch deck was created

        Returns:
            PitchDeck instance

        Raises:
            FileNotFoundError: If file does not exist
            SequoiaParseError: If validation fails
            ValueError: If no version in frontmatter

        Example:
            >>> parser = SequoiaParser()
            >>> deck = parser.parse_pitch_deck(Path(".specify/deck/pitch-deck.md"))
            >>> len(deck.sections)
            10
        """
        # Parse using existing PitchDeck.parse method
        deck = PitchDeck.parse(file_path)

        # Update source mode
        deck.source_mode = source_mode

        # Validate Sequoia structure
        is_valid, missing_sections = deck.validate_sequoia_structure()

        if not is_valid:
            raise SequoiaParseError(
                f"Pitch deck missing required Sequoia sections: {', '.join(missing_sections)}\n"
                f"Expected 10 sections: {', '.join([s.value for s in SequoiaSectionType])}"
            )

        return deck

    def validate_section_content(self, section: PitchDeckSection) -> list[str]:
        """Validate section has meaningful content.

        Args:
            section: Pitch deck section to validate

        Returns:
            List of validation warnings (empty if valid)

        Example:
            >>> parser = SequoiaParser()
            >>> section = PitchDeckSection("problem", "Problem", "[TBD]", 0, 1)
            >>> warnings = parser.validate_section_content(section)
            >>> len(warnings) > 0
            True
        """
        warnings = []

        # Check if empty
        if section.is_empty():
            warnings.append(f"Section '{section.section_id}' is empty or contains only placeholders")

        # Check for vagueness
        vague_indicators = section.detect_vagueness()
        if vague_indicators:
            warnings.append(
                f"Section '{section.section_id}' contains vague content: {', '.join(vague_indicators)}"
            )

        # Check word count (minimum 10 words for substantive sections)
        word_count = section.get_word_count()
        if word_count < 10 and section.section_id not in ["company-purpose"]:
            # Company purpose can be short (single sentence)
            warnings.append(
                f"Section '{section.section_id}' has low word count ({word_count} words)"
            )

        return warnings

    def validate_all_sections(self, deck: PitchDeck) -> dict[str, list[str]]:
        """Validate content of all sections in pitch deck.

        Args:
            deck: Pitch deck to validate

        Returns:
            Dictionary mapping section_id to list of warnings

        Example:
            >>> parser = SequoiaParser()
            >>> deck = parser.parse_pitch_deck(Path(".specify/deck/pitch-deck.md"))
            >>> warnings_by_section = parser.validate_all_sections(deck)
            >>> all(len(w) == 0 for w in warnings_by_section.values())
            True
        """
        warnings_by_section = {}

        for section in deck.sections:
            warnings = self.validate_section_content(section)
            if warnings:
                warnings_by_section[section.section_id] = warnings

        return warnings_by_section

    def extract_section_text(self, deck: PitchDeck, section_id: str) -> str:
        """Extract text content from specific section.

        Args:
            deck: Pitch deck instance
            section_id: Section identifier

        Returns:
            Section content text (empty string if not found)

        Example:
            >>> parser = SequoiaParser()
            >>> deck = parser.parse_pitch_deck(Path(".specify/deck/pitch-deck.md"))
            >>> problem_text = parser.extract_section_text(deck, "problem")
            >>> len(problem_text) > 0
            True
        """
        section = deck.get_section(section_id)
        if section is None:
            return ""
        return section.content

    def get_sections_for_constitution(
        self, deck: PitchDeck, constitution_type: str
    ) -> list[PitchDeckSection]:
        """Get all pitch deck sections that map to a specific constitution.

        Args:
            deck: Pitch deck instance
            constitution_type: Constitution filename (e.g., 'company-constitution.md')

        Returns:
            List of PitchDeckSection objects

        Example:
            >>> parser = SequoiaParser()
            >>> deck = parser.parse_pitch_deck(Path(".specify/deck/pitch-deck.md"))
            >>> company_sections = parser.get_sections_for_constitution(
            ...     deck, "company-constitution.md"
            ... )
            >>> len(company_sections) >= 3  # company-purpose, problem, why-now
            True
        """
        from ..models.sequoia_section import SECTION_CONSTITUTION_MAP

        # Reverse lookup: find all section types that map to this constitution
        relevant_section_types = [
            section_type
            for section_type, constitution in SECTION_CONSTITUTION_MAP.items()
            if constitution == constitution_type
        ]

        # Get sections from deck
        sections = []
        for section_type in relevant_section_types:
            section = deck.get_section(section_type.value)
            if section:
                sections.append(section)

        return sections

    def detect_custom_sections(self, deck: PitchDeck) -> list[PitchDeckSection]:
        """Detect sections not in Sequoia 10-section template.

        Args:
            deck: Pitch deck instance

        Returns:
            List of custom (non-Sequoia) sections

        Example:
            >>> parser = SequoiaParser()
            >>> deck = parser.parse_pitch_deck(Path(".specify/deck/pitch-deck.md"))
            >>> custom = parser.detect_custom_sections(deck)
            >>> # May return additional sections like "Traction", "Partners", etc.
        """
        sequoia_ids = {section.value for section in SequoiaSectionType}
        custom_sections = [
            section for section in deck.sections if section.section_id not in sequoia_ids
        ]
        return custom_sections
