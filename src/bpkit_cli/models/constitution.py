"""Constitution models for BP-Kit quality commands."""

from enum import Enum
from pathlib import Path
from typing import Any

from ..core.markdown_parser import MarkdownLink, MarkdownParser
from ..core.version_tracker import VersionTracker


class ConstitutionType(str, Enum):
    """Type of constitution document."""

    STRATEGIC = "strategic"  # company, product, market, business
    FEATURE = "feature"  # feature constitutions (001-XXX.md)


class Principle:
    """Individual constitutional principle with traceability."""

    def __init__(
        self,
        principle_id: str,
        title: str,
        rule: str,
        source_link: str | None = None,
        test_criteria: str | None = None,
    ) -> None:
        """Initialize principle.

        Args:
            principle_id: Unique identifier (e.g., 'principle-1', 'FP1')
            title: Brief principle name
            rule: What MUST or MUST NOT happen
            source_link: Link to upstream source (pitch deck or strategic constitution)
            test_criteria: How to verify compliance
        """
        self.principle_id = principle_id
        self.title = title
        self.rule = rule
        self.source_link = source_link
        self.test_criteria = test_criteria

    def is_testable(self) -> bool:
        """Check if principle has specific test criteria.

        Returns:
            True if test_criteria is non-empty
        """
        return bool(self.test_criteria and self.test_criteria.strip())

    def has_valid_source(self) -> bool:
        """Check if principle has a source link.

        Returns:
            True if source_link is non-empty
        """
        return bool(self.source_link and self.source_link.strip())

    def __repr__(self) -> str:
        return f"Principle(id='{self.principle_id}', title='{self.title}')"


class Constitution:
    """Strategic or feature constitution document with principles and links."""

    def __init__(
        self,
        file_path: Path,
        constitution_type: ConstitutionType,
        name: str,
        version: str,
        principles: list[Principle],
        upstream_links: list[MarkdownLink],
        downstream_links: list[MarkdownLink],
    ) -> None:
        """Initialize constitution.

        Args:
            file_path: Path to constitution markdown file
            constitution_type: STRATEGIC or FEATURE
            name: Constitution name (e.g., 'company-constitution', '001-user-management')
            version: Semantic version string
            principles: List of constitutional principles
            upstream_links: Links to pitch deck or strategic constitutions
            downstream_links: Links from features (for strategic constitutions)
        """
        self.file_path = file_path
        self.constitution_type = constitution_type
        self.name = name
        self.version = version
        self.principles = principles
        self.upstream_links = upstream_links
        self.downstream_links = downstream_links
        self._parser = MarkdownParser()
        self._version_tracker = VersionTracker()

    @classmethod
    def parse(cls, file_path: Path) -> "Constitution":
        """Parse constitution from markdown file.

        Args:
            file_path: Path to constitution markdown file

        Returns:
            Constitution instance

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format is invalid

        Example:
            >>> const = Constitution.parse(Path(".specify/memory/company-constitution.md"))
            >>> const.constitution_type
            <ConstitutionType.STRATEGIC: 'strategic'>
        """
        parser = MarkdownParser()
        version_tracker = VersionTracker()

        # Read file
        content = parser.parse_file(file_path)

        # Extract version
        version = version_tracker.extract_version_from_frontmatter(file_path)
        if version is None:
            # Default to 1.0.0 if no version
            version = "1.0.0"

        # Determine constitution type based on path
        if "/memory/" in str(file_path):
            constitution_type = ConstitutionType.STRATEGIC
        elif "/features/" in str(file_path):
            constitution_type = ConstitutionType.FEATURE
        else:
            # Default based on filename pattern
            if file_path.stem.startswith(("001-", "002-", "003-")):
                constitution_type = ConstitutionType.FEATURE
            else:
                constitution_type = ConstitutionType.STRATEGIC

        # Extract name from filename
        name = file_path.stem

        # Extract all links (upstream traceability)
        all_links = parser.extract_links(content)

        # Filter upstream links (references to pitch deck or strategic constitutions)
        upstream_links = [
            link
            for link in all_links
            if ("/deck/" in link.url or "/memory/" in link.url or "pitch-deck.md" in link.url)
        ]

        # Downstream links would be populated by analyze command
        downstream_links: list[MarkdownLink] = []

        # Extract principles (simplified - look for principle IDs in headings)
        sections = parser.extract_sections(content)
        principles: list[Principle] = []

        for section in sections:
            # Check if section looks like a principle
            section_id_lower = section.section_id.lower()
            if (
                "principle" in section_id_lower
                or section_id_lower.startswith("fp")
                or section_id_lower.startswith("sp")
            ):
                # Extract rule (look for MUST or MUST NOT)
                rule = ""
                for line in section.content.split("\n"):
                    if "MUST" in line.upper():
                        rule = line.strip()
                        break

                principle = Principle(
                    principle_id=section.section_id,
                    title=section.title,
                    rule=rule or section.content[:100],  # First 100 chars as fallback
                    source_link=None,  # Would need deeper parsing
                    test_criteria=None,  # Would need deeper parsing
                )
                principles.append(principle)

        return cls(
            file_path=file_path,
            constitution_type=constitution_type,
            name=name,
            version=version,
            principles=principles,
            upstream_links=upstream_links,
            downstream_links=downstream_links,
        )

    def get_principle(self, principle_id: str) -> Principle | None:
        """Get principle by ID.

        Args:
            principle_id: Principle identifier

        Returns:
            Principle if found, None otherwise
        """
        for principle in self.principles:
            if principle.principle_id == principle_id:
                return principle
        return None

    def validate_links(self) -> list[str]:
        """Validate all traceability links.

        Returns:
            List of error messages for broken links

        Note:
            This is a basic implementation. Full validation happens in LinkValidator.
        """
        errors: list[str] = []

        for link in self.upstream_links:
            # Check if link URL looks valid (has a path)
            if not link.url or link.url.startswith("#"):
                errors.append(
                    f"Line {link.line_number}: Broken link - missing file path in '{link.url}'"
                )

        return errors

    def __repr__(self) -> str:
        return (
            f"Constitution(name='{self.name}', type={self.constitution_type.value}, "
            f"principles={len(self.principles)}, version='{self.version}')"
        )
