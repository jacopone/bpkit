"""Pitch deck models for BP-Kit quality commands."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..core.markdown_parser import MarkdownParser, MarkdownSection
from ..core.version_tracker import BumpType, VersionTracker


class SourceMode(str, Enum):
    """Mode by which pitch deck was created."""

    INTERACTIVE = "interactive"
    """Created via interactive Q&A"""

    FROM_FILE = "from-file"
    """Parsed from existing markdown file"""

    FROM_PDF = "from-pdf"
    """Extracted from PDF and converted to markdown"""

    MANUAL = "manual"
    """Created manually by user"""


class PitchDeckSection:
    """Individual section within a pitch deck."""

    def __init__(
        self,
        section_id: str,
        title: str,
        content: str,
        line_start: int,
        line_end: int,
    ) -> None:
        """Initialize pitch deck section.

        Args:
            section_id: Section identifier (e.g., 'problem', 'solution')
            title: Section title
            content: Section content
            line_start: Starting line number
            line_end: Ending line number
        """
        self.section_id = section_id
        self.title = title
        self.content = content
        self.line_start = line_start
        self.line_end = line_end

    def is_empty(self) -> bool:
        """Check if section has only whitespace or placeholders.

        Returns:
            True if section is empty or contains only placeholders
        """
        if not self.content or not self.content.strip():
            return True

        # Check for common placeholder patterns
        placeholders = ["[tbd]", "[x]", "[todo]", "[needs input]", "..."]
        content_lower = self.content.lower().strip()

        return any(content_lower == p or content_lower.startswith(p) for p in placeholders)

    def detect_vagueness(self) -> list[str]:
        """Detect vague phrases or incomplete content in section.

        Returns:
            List of vague indicators found in content

        Example:
            >>> section = PitchDeckSection("problem", "Problem", "[TBD]", 0, 1)
            >>> section.detect_vagueness()
            ['[TBD]']
        """
        vague_indicators: list[str] = []
        content_lower = self.content.lower()

        # Patterns indicating vagueness or incompleteness
        patterns = [
            "[tbd]",
            "[x]",
            "[todo]",
            "[needs clarification]",
            "[needs input]",
            "tbd",
            "to be determined",
            "coming soon",
            "...",
            "etc.",
            "and more",
            "and so on",
        ]

        for pattern in patterns:
            if pattern in content_lower:
                # Find actual occurrence with original case
                import re

                match = re.search(re.escape(pattern), self.content, re.IGNORECASE)
                if match:
                    vague_indicators.append(match.group())

        return vague_indicators

    def get_word_count(self) -> int:
        """Get word count of section content.

        Returns:
            Number of words in content
        """
        return len(self.content.split())

    def __repr__(self) -> str:
        return (
            f"PitchDeckSection(id='{self.section_id}', title='{self.title}', "
            f"words={self.get_word_count()})"
        )


class PitchDeck:
    """Represents a pitch deck document with sections and version metadata."""

    def __init__(
        self,
        file_path: Path,
        version: str,
        sections: list[PitchDeckSection],
        last_modified: datetime | None = None,
        source_mode: SourceMode = SourceMode.MANUAL,
    ) -> None:
        """Initialize pitch deck.

        Args:
            file_path: Path to pitch deck markdown file
            version: Semantic version string
            sections: List of pitch deck sections
            last_modified: Last modification datetime (defaults to now)
            source_mode: How this pitch deck was created
        """
        self.file_path = file_path
        self.version = version
        self.sections = sections
        self.last_modified = last_modified or datetime.now()
        self.source_mode = source_mode
        self._parser = MarkdownParser()
        self._version_tracker = VersionTracker()

    @classmethod
    def parse(cls, file_path: Path) -> "PitchDeck":
        """Parse pitch deck from markdown file.

        Args:
            file_path: Path to pitch deck markdown file

        Returns:
            PitchDeck instance

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file has no version in frontmatter

        Example:
            >>> deck = PitchDeck.parse(Path(".specify/deck/pitch-deck.md"))
            >>> len(deck.sections)
            8
        """
        parser = MarkdownParser()
        version_tracker = VersionTracker()

        # Read file and extract version
        content = parser.parse_file(file_path)
        version = version_tracker.extract_version_from_frontmatter(file_path)

        if version is None:
            raise ValueError(f"Pitch deck {file_path} has no version in frontmatter")

        # Extract sections
        markdown_sections = parser.extract_sections(content)

        # Convert to PitchDeckSection objects
        sections = [
            PitchDeckSection(
                section_id=ms.section_id,
                title=ms.title,
                content=ms.content,
                line_start=ms.line_start,
                line_end=ms.line_end,
            )
            for ms in markdown_sections
        ]

        # Get last modified time
        try:
            last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
        except Exception:
            last_modified = datetime.now()

        return cls(
            file_path=file_path,
            version=version,
            sections=sections,
            last_modified=last_modified,
        )

    def get_section(self, section_id: str) -> PitchDeckSection | None:
        """Get section by ID.

        Args:
            section_id: Section identifier

        Returns:
            PitchDeckSection if found, None otherwise

        Example:
            >>> deck = PitchDeck.parse(Path(".specify/deck/pitch-deck.md"))
            >>> section = deck.get_section("problem")
            >>> section.title
            'Problem'
        """
        for section in self.sections:
            if section.section_id == section_id:
                return section
        return None

    def update_section(self, section_id: str, new_content: str) -> None:
        """Update section content in memory.

        Note: This only updates the in-memory representation. Call save() to persist.

        Args:
            section_id: Section identifier
            new_content: New content for the section

        Raises:
            ValueError: If section not found
        """
        section = self.get_section(section_id)
        if section is None:
            raise ValueError(f"Section '{section_id}' not found in pitch deck")

        section.content = new_content

    def bump_version(self, bump_type: BumpType) -> str:
        """Bump version and return new version string.

        Args:
            bump_type: Type of version bump (MAJOR, MINOR, PATCH)

        Returns:
            New version string

        Example:
            >>> deck = PitchDeck.parse(Path(".specify/deck/pitch-deck.md"))
            >>> deck.version
            '1.0.0'
            >>> deck.bump_version(BumpType.PATCH)
            '1.0.1'
            >>> deck.version
            '1.0.1'
        """
        new_version = self._version_tracker.bump_version(self.version, bump_type)
        self.version = new_version
        return new_version

    def save(self) -> None:
        """Save pitch deck to file, updating version in frontmatter.

        Raises:
            FileNotFoundError: If file no longer exists
            IOError: If file cannot be written
        """
        # Update version in frontmatter
        try:
            self._version_tracker.update_version_in_frontmatter(self.file_path, self.version)
        except Exception as e:
            raise IOError(f"Failed to update version in {self.file_path}: {e}") from e

        # Note: Section content updates require manual markdown reconstruction
        # For now, we only update version. Section updates would require
        # a more sophisticated approach to preserve formatting.

    def validate_sequoia_structure(self) -> tuple[bool, list[str]]:
        """Validate that pitch deck conforms to Sequoia 10-section structure.

        Returns:
            Tuple of (is_valid, list of missing sections)

        Example:
            >>> deck = PitchDeck.parse(Path(".specify/deck/pitch-deck.md"))
            >>> is_valid, missing = deck.validate_sequoia_structure()
            >>> is_valid
            True
        """
        from .sequoia_section import SequoiaSectionType

        # Expected section IDs from Sequoia template
        expected_sections = {section.value for section in SequoiaSectionType}

        # Actual section IDs in pitch deck
        actual_sections = {section.section_id for section in self.sections}

        # Find missing sections
        missing_sections = expected_sections - actual_sections

        is_valid = len(missing_sections) == 0
        return is_valid, sorted(missing_sections)

    def get_sequoia_sections(self) -> list[tuple[str, PitchDeckSection | None]]:
        """Get all Sequoia sections in canonical order.

        Returns:
            List of (section_id, PitchDeckSection or None) tuples

        Example:
            >>> deck = PitchDeck.parse(Path(".specify/deck/pitch-deck.md"))
            >>> sections = deck.get_sequoia_sections()
            >>> len(sections)
            10
        """
        from .sequoia_section import SequoiaSectionType

        result = []
        for section_type in SequoiaSectionType:
            section = self.get_section(section_type.value)
            result.append((section_type.value, section))

        return result

    def __repr__(self) -> str:
        return (
            f"PitchDeck(version='{self.version}', sections={len(self.sections)}, "
            f"file='{self.file_path.name}', mode={self.source_mode.value})"
        )
