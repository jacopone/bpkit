"""Traceability link models for BP-Kit quality commands."""

from enum import Enum
from pathlib import Path
from typing import Any


class LinkType(str, Enum):
    """Type of traceability link."""

    PITCH_TO_STRATEGIC = "pitch_to_strategic"  # Deck → Strategic constitution
    STRATEGIC_TO_PITCH = "strategic_to_pitch"  # Strategic → Deck (reverse)
    STRATEGIC_TO_FEATURE = "strategic_to_feature"  # Strategic → Feature constitution
    FEATURE_TO_STRATEGIC = "feature_to_strategic"  # Feature → Strategic (reverse)
    FEATURE_TO_PITCH = "feature_to_pitch"  # Feature → Deck (direct)


class LinkValidationState(str, Enum):
    """State of link validation."""

    VALID = "valid"  # Target file and section both exist
    BROKEN_FILE = "broken_file"  # Target file does not exist
    BROKEN_SECTION = "broken_section"  # File exists but section does not
    MISSING_SOURCE = "missing_source"  # Source file does not exist


class LinkValidationResult:
    """Result of validating a traceability link."""

    def __init__(
        self,
        state: LinkValidationState,
        message: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        """Initialize validation result.

        Args:
            state: Validation state
            message: Human-readable message
            suggestion: Suggestion for fixing broken link
        """
        self.state = state
        self.message = message
        self.suggestion = suggestion

    def is_valid(self) -> bool:
        """Check if link is valid.

        Returns:
            True if state is VALID
        """
        return self.state == LinkValidationState.VALID

    def __repr__(self) -> str:
        return f"LinkValidationResult(state={self.state.value}, message='{self.message}')"


class TraceabilityLink:
    """Reference from one document/section to another."""

    def __init__(
        self,
        source_file: Path,
        source_line: int,
        target_file: Path | str,
        target_section: str | None = None,
        link_text: str | None = None,
        link_type: LinkType | None = None,
    ) -> None:
        """Initialize traceability link.

        Args:
            source_file: File containing the link
            source_line: Line number of link in source file
            target_file: Referenced file (absolute or relative path)
            target_section: Section ID in target file (e.g., '#principle-1')
            link_text: Display text in markdown link
            link_type: Type of link (pitch→strategic, strategic→feature, etc.)
        """
        self.source_file = source_file
        self.source_line = source_line
        self.target_file = Path(target_file) if isinstance(target_file, str) else target_file
        self.target_section = target_section
        self.link_text = link_text
        self.link_type = link_type
        self._validation_result: LinkValidationResult | None = None

    @classmethod
    def from_markdown_link(
        cls, source_file: Path, url: str, line_number: int, link_text: str | None = None
    ) -> "TraceabilityLink":
        """Create TraceabilityLink from markdown link URL.

        Parses markdown link format: ../path/file.md#section-id

        Args:
            source_file: File containing the link
            url: Markdown link URL
            line_number: Line number in source file
            link_text: Link display text

        Returns:
            TraceabilityLink instance

        Example:
            >>> link = TraceabilityLink.from_markdown_link(
            ...     Path("features/001.md"),
            ...     "../memory/company.md#principle-1",
            ...     10,
            ...     "Company Principle 1"
            ... )
            >>> link.target_section
            'principle-1'
        """
        # Split URL into file path and section
        if "#" in url:
            file_part, section_part = url.split("#", 1)
            target_section = section_part
        else:
            file_part = url
            target_section = None

        # Resolve relative path
        target_file = source_file.parent / file_part if file_part else source_file

        # Infer link type based on paths
        link_type = cls._infer_link_type(source_file, target_file)

        return cls(
            source_file=source_file,
            source_line=line_number,
            target_file=target_file,
            target_section=target_section,
            link_text=link_text,
            link_type=link_type,
        )

    @staticmethod
    def _infer_link_type(source_file: Path, target_file: Path) -> LinkType:
        """Infer link type from source and target file paths.

        Args:
            source_file: Source file path
            target_file: Target file path

        Returns:
            Inferred LinkType
        """
        source_str = str(source_file)
        target_str = str(target_file)

        # Check source location
        source_is_strategic = "/memory/" in source_str or "constitution.md" in source_str
        source_is_feature = "/features/" in source_str
        source_is_deck = "/deck/" in source_str or "pitch-deck.md" in source_str

        # Check target location
        target_is_strategic = "/memory/" in target_str or "constitution.md" in target_str
        target_is_feature = "/features/" in target_str
        target_is_deck = "/deck/" in target_str or "pitch-deck.md" in target_str

        # Determine link type
        if source_is_deck and target_is_strategic:
            return LinkType.PITCH_TO_STRATEGIC
        elif source_is_strategic and target_is_deck:
            return LinkType.STRATEGIC_TO_PITCH
        elif source_is_strategic and target_is_feature:
            return LinkType.STRATEGIC_TO_FEATURE
        elif source_is_feature and target_is_strategic:
            return LinkType.FEATURE_TO_STRATEGIC
        elif source_is_feature and target_is_deck:
            return LinkType.FEATURE_TO_PITCH
        else:
            # Default
            return LinkType.FEATURE_TO_STRATEGIC

    def validate(self) -> LinkValidationResult:
        """Validate this traceability link.

        Checks:
        1. Source file exists (should always be true)
        2. Target file exists
        3. If target_section specified, section exists in target

        Returns:
            LinkValidationResult with validation state

        Example:
            >>> link = TraceabilityLink(
            ...     Path("features/001.md"),
            ...     10,
            ...     Path(".specify/memory/company.md"),
            ...     "principle-1"
            ... )
            >>> result = link.validate()
            >>> result.is_valid()
            True
        """
        # Check source file exists
        if not self.source_file.exists():
            result = LinkValidationResult(
                state=LinkValidationState.MISSING_SOURCE,
                message=f"Source file does not exist: {self.source_file}",
            )
            self._validation_result = result
            return result

        # Check target file exists
        if not self.target_file.exists():
            result = LinkValidationResult(
                state=LinkValidationState.BROKEN_FILE,
                message=f"Target file does not exist: {self.target_file}",
                suggestion=f"Create {self.target_file} or update link in {self.source_file}:{self.source_line}",
            )
            self._validation_result = result
            return result

        # If target_section specified, check it exists
        if self.target_section:
            # Import here to avoid circular dependency
            from ..core.markdown_parser import MarkdownParser

            parser = MarkdownParser()
            try:
                content = parser.parse_file(self.target_file)
                heading_ids = parser.extract_heading_ids(content)

                if self.target_section not in heading_ids:
                    available = ", ".join(list(heading_ids.keys())[:5])
                    result = LinkValidationResult(
                        state=LinkValidationState.BROKEN_SECTION,
                        message=f"Section '#{self.target_section}' not found in {self.target_file}",
                        suggestion=f"Available sections: {available}",
                    )
                    self._validation_result = result
                    return result
            except Exception as e:
                result = LinkValidationResult(
                    state=LinkValidationState.BROKEN_FILE,
                    message=f"Failed to read target file {self.target_file}: {e}",
                )
                self._validation_result = result
                return result

        # All checks passed
        result = LinkValidationResult(
            state=LinkValidationState.VALID, message="Link is valid"
        )
        self._validation_result = result
        return result

    def get_target(self) -> str | None:
        """Get target content (section content if specified, else whole file).

        Returns:
            Target content as string, or None if target invalid

        Note:
            This is a simplified implementation. Full content extraction
            would require more sophisticated parsing.
        """
        if not self.target_file.exists():
            return None

        try:
            from ..core.markdown_parser import MarkdownParser

            parser = MarkdownParser()
            content = parser.parse_file(self.target_file)

            if self.target_section:
                # Extract specific section
                sections = parser.extract_sections(content)
                for section in sections:
                    if section.section_id == self.target_section:
                        return section.content

                return None  # Section not found
            else:
                return content  # Return whole file

        except Exception:
            return None

    def __repr__(self) -> str:
        section = f"#{self.target_section}" if self.target_section else ""
        return (
            f"TraceabilityLink({self.source_file.name}:{self.source_line} → "
            f"{self.target_file.name}{section})"
        )
