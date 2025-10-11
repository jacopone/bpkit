"""Markdown parsing utilities for BP-Kit quality commands."""

from pathlib import Path
from typing import Any

from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode


class MarkdownSection:
    """Represents a section in a markdown document."""

    def __init__(
        self,
        section_id: str,
        title: str,
        content: str,
        line_start: int,
        line_end: int,
        level: int,
    ) -> None:
        self.section_id = section_id
        self.title = title
        self.content = content
        self.line_start = line_start
        self.line_end = line_end
        self.level = level

    def __repr__(self) -> str:
        return (
            f"MarkdownSection(id='{self.section_id}', title='{self.title}', "
            f"lines={self.line_start}-{self.line_end})"
        )


class MarkdownLink:
    """Represents a markdown link [text](url)."""

    def __init__(self, text: str, url: str, line_number: int) -> None:
        self.text = text
        self.url = url
        self.line_number = line_number

    def __repr__(self) -> str:
        return f"MarkdownLink(text='{self.text}', url='{self.url}', line={self.line_number})"


class MarkdownParser:
    """Parser for markdown documents using markdown-it-py."""

    def __init__(self) -> None:
        """Initialize the parser with CommonMark + GFM extensions."""
        self.md = MarkdownIt("commonmark", {"linkify": True, "typographer": True})
        self.md.enable(["table", "strikethrough"])

    def parse_file(self, file_path: Path) -> str:
        """Read and return content of markdown file.

        Args:
            file_path: Path to markdown file

        Returns:
            File content as string

        Raises:
            FileNotFoundError: If file does not exist
            IOError: If file cannot be read
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {file_path}")

        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise IOError(f"Failed to read markdown file {file_path}: {e}") from e

    def extract_sections(self, content: str) -> list[MarkdownSection]:
        """Extract sections from markdown content based on headings.

        Sections are defined by headings (# H1, ## H2, etc.). Each section includes
        the heading and all content until the next heading of the same or higher level.

        Args:
            content: Markdown content as string

        Returns:
            List of MarkdownSection objects

        Example:
            >>> parser = MarkdownParser()
            >>> sections = parser.extract_sections("# Title\\n\\nContent\\n\\n## Subtitle\\n\\nMore")
            >>> len(sections)
            2
        """
        tokens = self.md.parse(content)
        sections: list[MarkdownSection] = []
        lines = content.split("\n")

        # Track current section being built
        current_heading: dict[str, Any] | None = None
        current_content_lines: list[str] = []

        for i, token in enumerate(tokens):
            if token.type == "heading_open":
                # Save previous section if exists
                if current_heading is not None:
                    sections.append(self._build_section(current_heading, current_content_lines))
                    current_content_lines = []

                # Start new section
                level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
                line_number = token.map[0] if token.map else 0

                # Get heading text from next token
                heading_text = ""
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    heading_text = tokens[i + 1].content

                current_heading = {
                    "level": level,
                    "title": heading_text,
                    "section_id": self._heading_to_id(heading_text),
                    "line_start": line_number,
                }

            elif current_heading is not None and token.map:
                # Add content lines to current section
                start_line, end_line = token.map
                for line_num in range(start_line, end_line):
                    if line_num < len(lines):
                        current_content_lines.append(lines[line_num])

        # Save last section
        if current_heading is not None:
            sections.append(self._build_section(current_heading, current_content_lines))

        return sections

    def _build_section(
        self, heading_info: dict[str, Any], content_lines: list[str]
    ) -> MarkdownSection:
        """Build a MarkdownSection from heading info and content lines."""
        content = "\n".join(content_lines)
        line_end = heading_info["line_start"] + len(content_lines)

        return MarkdownSection(
            section_id=heading_info["section_id"],
            title=heading_info["title"],
            content=content.strip(),
            line_start=heading_info["line_start"],
            line_end=line_end,
            level=heading_info["level"],
        )

    def extract_heading_ids(self, content: str) -> dict[str, int]:
        """Extract all heading IDs and their line numbers from markdown content.

        Args:
            content: Markdown content as string

        Returns:
            Dictionary mapping section IDs to line numbers

        Example:
            >>> parser = MarkdownParser()
            >>> ids = parser.extract_heading_ids("# Company Purpose\\n\\n## Problem")
            >>> ids
            {'company-purpose': 0, 'problem': 2}
        """
        tokens = self.md.parse(content)
        heading_ids: dict[str, int] = {}

        for i, token in enumerate(tokens):
            if token.type == "heading_open":
                line_number = token.map[0] if token.map else 0

                # Get heading text from next token
                heading_text = ""
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    heading_text = tokens[i + 1].content

                section_id = self._heading_to_id(heading_text)
                heading_ids[section_id] = line_number

        return heading_ids

    def extract_links(self, content: str) -> list[MarkdownLink]:
        """Extract all markdown links from content.

        Args:
            content: Markdown content as string

        Returns:
            List of MarkdownLink objects with text, URL, and line number

        Example:
            >>> parser = MarkdownParser()
            >>> links = parser.extract_links("[text](../file.md#section)")
            >>> links[0].url
            '../file.md#section'
        """
        tokens = self.md.parse(content)
        links: list[MarkdownLink] = []

        for i, token in enumerate(tokens):
            if token.type == "link_open":
                line_number = token.map[0] if token.map else 0
                href = token.attrGet("href") or ""

                # Get link text from next inline token
                link_text = ""
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    link_text = tokens[i + 1].content

                links.append(MarkdownLink(text=link_text, url=href, line_number=line_number))

        return links

    @staticmethod
    def _heading_to_id(heading: str) -> str:
        """Convert heading text to section ID (GitHub-style).

        Args:
            heading: Heading text

        Returns:
            Section ID in lowercase-with-dashes format

        Example:
            >>> MarkdownParser._heading_to_id("Company Purpose")
            'company-purpose'
            >>> MarkdownParser._heading_to_id("What's the Problem?")
            'whats-the-problem'
        """
        # Convert to lowercase
        section_id = heading.lower()

        # Replace spaces and special chars with dashes
        import re

        section_id = re.sub(r"[^\w\s-]", "", section_id)
        section_id = re.sub(r"[-\s]+", "-", section_id)

        # Remove leading/trailing dashes
        return section_id.strip("-")
