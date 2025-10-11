"""Decomposition result models for BP-Kit."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class DecompositionMode(str, Enum):
    """Mode of pitch deck decomposition."""

    INTERACTIVE = "interactive"
    FROM_FILE = "from-file"
    FROM_PDF = "from-pdf"


@dataclass
class DecompositionCounts:
    """Statistics from decomposition operation."""

    strategic_constitutions: int = 0
    """Number of strategic constitutions generated (expected: 4)"""

    feature_constitutions: int = 0
    """Number of feature constitutions generated (expected: 5-10)"""

    total_principles: int = 0
    """Total principles extracted across all constitutions"""

    traceability_links: int = 0
    """Total bidirectional links created"""

    entities_extracted: int = 0
    """Number of entities detected in features"""

    success_criteria_derived: int = 0
    """Number of success criteria with type=derived"""

    success_criteria_placeholder: int = 0
    """Number of success criteria with type=placeholder"""


@dataclass
class DecompositionWarning:
    """Non-blocking issue detected during decomposition."""

    code: str
    """Warning code (e.g., 'LOW_FEATURE_COUNT')"""

    message: str
    """Human-readable warning message"""

    section_id: str | None = None
    """Related pitch deck section (if applicable)"""

    suggestion: str | None = None
    """Suggested action to resolve warning"""


@dataclass
class DecompositionError:
    """Blocking error that prevented decomposition completion."""

    code: str
    """Error code (e.g., 'MISSING_SECTION')"""

    message: str
    """Human-readable error message"""

    section_id: str | None = None
    """Related pitch deck section (if applicable)"""

    recoverable: bool = False
    """Whether decomposition can continue after fixing this error"""


@dataclass
class DecompositionResult:
    """Complete result of pitch deck decomposition operation."""

    mode: DecompositionMode
    """Mode used for decomposition"""

    pitch_deck_path: Path
    """Path to pitch deck markdown file"""

    pitch_deck_version: str
    """Version assigned to pitch deck (SemVer)"""

    counts: DecompositionCounts = field(default_factory=DecompositionCounts)
    """Statistics from decomposition"""

    warnings: list[DecompositionWarning] = field(default_factory=list)
    """Non-blocking issues detected"""

    errors: list[DecompositionError] = field(default_factory=list)
    """Blocking errors encountered"""

    dry_run: bool = False
    """Whether this was a dry-run (no files written)"""

    changelog_entry: Path | None = None
    """Path to generated changelog entry (if created)"""

    def is_success(self) -> bool:
        """Check if decomposition succeeded.

        Returns:
            True if no blocking errors, False otherwise
        """
        return len(self.errors) == 0

    def has_warnings(self) -> bool:
        """Check if decomposition generated warnings.

        Returns:
            True if warnings present
        """
        return len(self.warnings) > 0

    def get_summary(self) -> str:
        """Generate human-readable summary of decomposition.

        Returns:
            Multi-line summary string

        Example:
            >>> result = DecompositionResult(
            ...     mode=DecompositionMode.INTERACTIVE,
            ...     pitch_deck_path=Path(".specify/deck/pitch-deck.md"),
            ...     pitch_deck_version="1.0.0"
            ... )
            >>> result.counts.strategic_constitutions = 4
            >>> result.counts.feature_constitutions = 7
            >>> summary = result.get_summary()
            >>> "4 strategic" in summary
            True
        """
        lines = [
            f"Decomposition Mode: {self.mode.value}",
            f"Pitch Deck: {self.pitch_deck_path.name} (v{self.pitch_deck_version})",
            "",
            "Results:",
            f"  - Strategic Constitutions: {self.counts.strategic_constitutions}",
            f"  - Feature Constitutions: {self.counts.feature_constitutions}",
            f"  - Total Principles: {self.counts.total_principles}",
            f"  - Traceability Links: {self.counts.traceability_links}",
            f"  - Entities Extracted: {self.counts.entities_extracted}",
            f"  - Success Criteria (Derived): {self.counts.success_criteria_derived}",
            f"  - Success Criteria (Placeholder): {self.counts.success_criteria_placeholder}",
        ]

        if self.warnings:
            lines.append("")
            lines.append(f"Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                lines.append(f"  - [{warning.code}] {warning.message}")

        if self.errors:
            lines.append("")
            lines.append(f"Errors: {len(self.errors)}")
            for error in self.errors:
                lines.append(f"  - [{error.code}] {error.message}")

        if self.dry_run:
            lines.append("")
            lines.append("(Dry-run mode - no files written)")

        return "\n".join(lines)

    def __repr__(self) -> str:
        status = "SUCCESS" if self.is_success() else "FAILED"
        return (
            f"DecompositionResult(mode={self.mode.value}, "
            f"status={status}, "
            f"features={self.counts.feature_constitutions})"
        )
