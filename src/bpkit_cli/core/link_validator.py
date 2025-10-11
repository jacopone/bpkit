"""Link validation utilities for BP-Kit quality commands."""

import asyncio
from pathlib import Path
from typing import Any

from ..core.markdown_parser import MarkdownLink, MarkdownParser
from ..models.traceability import LinkValidationResult, LinkValidationState, TraceabilityLink


class LinkValidator:
    """Validate traceability links in constitutions."""

    def __init__(self) -> None:
        """Initialize link validator."""
        self._parser = MarkdownParser()

    def extract_links(self, file_path: Path) -> list[TraceabilityLink]:
        """Extract all traceability links from a markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            List of TraceabilityLink objects

        Example:
            >>> validator = LinkValidator()
            >>> links = validator.extract_links(Path(".specify/memory/company.md"))
            >>> len(links)
            5
        """
        try:
            content = self._parser.parse_file(file_path)
        except Exception:
            return []

        markdown_links = self._parser.extract_links(content)
        traceability_links: list[TraceabilityLink] = []

        for md_link in markdown_links:
            try:
                link = TraceabilityLink.from_markdown_link(
                    source_file=file_path,
                    url=md_link.url,
                    line_number=md_link.line_number,
                    link_text=md_link.text,
                )
                traceability_links.append(link)
            except Exception:
                # Skip invalid links
                continue

        return traceability_links

    def validate_link(self, link: TraceabilityLink) -> LinkValidationResult:
        """Validate a single traceability link.

        Args:
            link: TraceabilityLink to validate

        Returns:
            LinkValidationResult with validation state

        Example:
            >>> validator = LinkValidator()
            >>> link = TraceabilityLink(
            ...     Path("features/001.md"),
            ...     10,
            ...     Path(".specify/memory/company.md"),
            ...     "principle-1"
            ... )
            >>> result = validator.validate_link(link)
            >>> result.is_valid()
            True
        """
        return link.validate()

    async def validate_all_links_async(
        self, links: list[TraceabilityLink]
    ) -> list[tuple[TraceabilityLink, LinkValidationResult]]:
        """Validate all links in parallel using asyncio.

        Args:
            links: List of TraceabilityLink objects

        Returns:
            List of (link, result) tuples

        Note:
            This is async to enable parallel validation for performance.
            100+ links can be validated in <500ms.
        """

        async def validate_one(link: TraceabilityLink) -> tuple[TraceabilityLink, LinkValidationResult]:
            # Run validation in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.validate_link, link)
            return (link, result)

        tasks = [validate_one(link) for link in links]
        return await asyncio.gather(*tasks)

    def validate_all_links(
        self, links: list[TraceabilityLink]
    ) -> list[tuple[TraceabilityLink, LinkValidationResult]]:
        """Validate all links (synchronous wrapper for async method).

        Args:
            links: List of TraceabilityLink objects

        Returns:
            List of (link, result) tuples

        Example:
            >>> validator = LinkValidator()
            >>> links = [
            ...     TraceabilityLink(Path("f1.md"), 1, Path("target.md"), "section-1"),
            ...     TraceabilityLink(Path("f2.md"), 1, Path("target.md"), "section-2"),
            ... ]
            >>> results = validator.validate_all_links(links)
            >>> len(results)
            2
        """
        return asyncio.run(self.validate_all_links_async(links))

    def extract_and_validate_file(
        self, file_path: Path
    ) -> list[tuple[TraceabilityLink, LinkValidationResult]]:
        """Extract and validate all links from a file.

        Convenience method that combines extract_links() and validate_all_links().

        Args:
            file_path: Path to markdown file

        Returns:
            List of (link, result) tuples

        Example:
            >>> validator = LinkValidator()
            >>> results = validator.extract_and_validate_file(Path(".specify/memory/company.md"))
            >>> broken = [r for r in results if not r[1].is_valid()]
            >>> len(broken)
            2
        """
        links = self.extract_links(file_path)
        if not links:
            return []

        return self.validate_all_links(links)

    def extract_and_validate_directory(
        self, directory: Path, pattern: str = "*.md"
    ) -> dict[Path, list[tuple[TraceabilityLink, LinkValidationResult]]]:
        """Extract and validate links from all markdown files in directory.

        Args:
            directory: Path to directory
            pattern: Glob pattern for files (default: "*.md")

        Returns:
            Dictionary mapping file paths to list of (link, result) tuples

        Example:
            >>> validator = LinkValidator()
            >>> results = validator.extract_and_validate_directory(Path(".specify/memory/"))
            >>> len(results)  # Number of files analyzed
            4
        """
        results: dict[Path, list[tuple[TraceabilityLink, LinkValidationResult]]] = {}

        if not directory.exists() or not directory.is_dir():
            return results

        for file_path in directory.glob(pattern):
            if file_path.is_file():
                file_results = self.extract_and_validate_file(file_path)
                if file_results:
                    results[file_path] = file_results

        return results

    def get_broken_links(
        self, results: list[tuple[TraceabilityLink, LinkValidationResult]]
    ) -> list[tuple[TraceabilityLink, LinkValidationResult]]:
        """Filter results to only broken links.

        Args:
            results: List of (link, result) tuples

        Returns:
            List of (link, result) tuples where link is broken

        Example:
            >>> validator = LinkValidator()
            >>> all_results = validator.extract_and_validate_file(Path("file.md"))
            >>> broken = validator.get_broken_links(all_results)
            >>> for link, result in broken:
            ...     print(f"Broken: {link} - {result.message}")
        """
        return [
            (link, result)
            for link, result in results
            if result.state != LinkValidationState.VALID
        ]

    def get_validation_summary(
        self, results: list[tuple[TraceabilityLink, LinkValidationResult]]
    ) -> dict[str, int]:
        """Get summary counts of validation results.

        Args:
            results: List of (link, result) tuples

        Returns:
            Dictionary with counts for each validation state

        Example:
            >>> validator = LinkValidator()
            >>> results = validator.extract_and_validate_file(Path("file.md"))
            >>> summary = validator.get_validation_summary(results)
            >>> summary
            {'valid': 10, 'broken_file': 2, 'broken_section': 1, 'missing_source': 0}
        """
        summary = {
            "valid": 0,
            "broken_file": 0,
            "broken_section": 0,
            "missing_source": 0,
        }

        for _, result in results:
            if result.state == LinkValidationState.VALID:
                summary["valid"] += 1
            elif result.state == LinkValidationState.BROKEN_FILE:
                summary["broken_file"] += 1
            elif result.state == LinkValidationState.BROKEN_SECTION:
                summary["broken_section"] += 1
            elif result.state == LinkValidationState.MISSING_SOURCE:
                summary["missing_source"] += 1

        return summary
