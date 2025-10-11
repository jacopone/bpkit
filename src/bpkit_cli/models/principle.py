"""Principle model for strategic and feature constitutions."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class Principle:
    """Represents a principle extracted from pitch deck.

    Principles can be strategic (high-level business/product guidance)
    or tactical (feature-specific implementation rules).
    """

    id: str
    """Unique identifier (e.g., 'principle-001')"""

    text: str
    """Full principle statement"""

    type: Literal["strategic", "tactical"]
    """Classification: strategic (for constitutions) or tactical (for features)"""

    source_section_id: str
    """Pitch deck section this principle was extracted from"""

    rationale: str | None = None
    """Why this principle matters (optional)"""

    test: str | None = None
    """How to validate adherence to this principle (optional)"""

    confidence: float = 1.0
    """Extraction confidence (0.0-1.0), default 1.0 for manual"""

    extraction_method: Literal["heuristic", "manual", "derived"] = "heuristic"
    """How this principle was created"""

    def to_markdown(self, index: int) -> str:
        """Render principle as markdown section.

        Args:
            index: Principle number (1-indexed)

        Returns:
            Formatted markdown string

        Example:
            >>> p = Principle(
            ...     id="principle-001",
            ...     text="Dual Value Proposition",
            ...     type="strategic",
            ...     source_section_id="solution",
            ...     rationale="Marketplace requires balanced incentives",
            ...     test="User research shows ≥70% cite primary motivation"
            ... )
            >>> print(p.to_markdown(1))
            ## Principle 1: Dual Value Proposition
            <BLANKLINE>
            Dual Value Proposition
            <BLANKLINE>
            **Rationale**: Marketplace requires balanced incentives
            <BLANKLINE>
            **Test**: User research shows ≥70% cite primary motivation
            <BLANKLINE>
            **Source**: [`pitch-deck.md#solution`](../deck/pitch-deck.md#solution)
        """
        lines = [
            f"## Principle {index}: {self.text}",
            "",
            self.text,
            "",
        ]

        if self.rationale:
            lines.append(f"**Rationale**: {self.rationale}")
            lines.append("")

        if self.test:
            lines.append(f"**Test**: {self.test}")
            lines.append("")

        # Add source link
        lines.append(
            f"**Source**: [`pitch-deck.md#{self.source_section_id}`](../deck/pitch-deck.md#{self.source_section_id})"
        )

        return "\n".join(lines)

    def __repr__(self) -> str:
        return (
            f"Principle(id='{self.id}', type='{self.type}', "
            f"confidence={self.confidence:.2f}, method='{self.extraction_method}')"
        )
