"""Analysis report models for BP-Kit quality commands."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from rich.table import Table


class Severity(str, Enum):
    """Severity level for validation issues."""

    ERROR = "error"  # Blocks progression, must fix
    WARNING = "warning"  # Non-blocking, should fix
    INFO = "info"  # Informational, no action needed


class ValidationIssue:
    """Base class for validation issues."""

    def __init__(
        self,
        issue_id: str,
        severity: Severity,
        message: str,
        file_path: Path | None = None,
        line_number: int | None = None,
        suggestion: str | None = None,
    ) -> None:
        """Initialize validation issue.

        Args:
            issue_id: Unique issue ID (ERR001, WARN001, INFO001)
            severity: ERROR, WARNING, or INFO
            message: Human-readable description
            file_path: Affected file (optional)
            line_number: Specific line if applicable (optional)
            suggestion: How to fix (optional)
        """
        self.issue_id = issue_id
        self.severity = severity
        self.message = message
        self.file_path = file_path
        self.line_number = line_number
        self.suggestion = suggestion

    def format(self) -> str:
        """Format issue for console output.

        Returns:
            Formatted string with severity, location, and message
        """
        severity_str = f"[{self.severity.value.upper()}]"
        location = ""

        if self.file_path:
            location = f" {self.file_path}"
            if self.line_number:
                location += f":{self.line_number}"

        return f"{severity_str}{location}: {self.message}"

    def __repr__(self) -> str:
        return f"ValidationIssue(id='{self.issue_id}', severity={self.severity.value})"


class ValidationError(ValidationIssue):
    """Error-level validation issue (blocks progression)."""

    def __init__(
        self,
        issue_id: str,
        message: str,
        file_path: Path | None = None,
        line_number: int | None = None,
        suggestion: str | None = None,
    ) -> None:
        super().__init__(issue_id, Severity.ERROR, message, file_path, line_number, suggestion)


class ValidationWarning(ValidationIssue):
    """Warning-level validation issue (should fix)."""

    def __init__(
        self,
        issue_id: str,
        message: str,
        file_path: Path | None = None,
        line_number: int | None = None,
        suggestion: str | None = None,
    ) -> None:
        super().__init__(issue_id, Severity.WARNING, message, file_path, line_number, suggestion)


class ValidationInfo(ValidationIssue):
    """Info-level validation issue (informational)."""

    def __init__(
        self,
        issue_id: str,
        message: str,
        file_path: Path | None = None,
        line_number: int | None = None,
        suggestion: str | None = None,
    ) -> None:
        super().__init__(issue_id, Severity.INFO, message, file_path, line_number, suggestion)


class AnalysisReport:
    """Results from /bp.analyze validation."""

    def __init__(
        self,
        report_id: str,
        timestamp: datetime,
        pitch_deck_version: str,
        constitutions_analyzed: int,
    ) -> None:
        """Initialize analysis report.

        Args:
            report_id: Unique report ID
            timestamp: When analysis was run
            pitch_deck_version: Version of pitch deck analyzed
            constitutions_analyzed: Count of constitutions checked
        """
        self.report_id = report_id
        self.timestamp = timestamp
        self.pitch_deck_version = pitch_deck_version
        self.constitutions_analyzed = constitutions_analyzed
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationWarning] = []
        self.info: list[ValidationInfo] = []

    def add_error(self, error: ValidationError) -> None:
        """Add error to report."""
        self.errors.append(error)

    def add_warning(self, warning: ValidationWarning) -> None:
        """Add warning to report."""
        self.warnings.append(warning)

    def add_info(self, info: ValidationInfo) -> None:
        """Add info to report."""
        self.info.append(info)

    def has_errors(self) -> bool:
        """Check if report has any errors.

        Returns:
            True if errors exist
        """
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if report has any warnings.

        Returns:
            True if warnings exist
        """
        return len(self.warnings) > 0

    def is_passing(self) -> bool:
        """Check if analysis passed (no errors).

        Returns:
            True if no errors (warnings are OK)
        """
        return not self.has_errors()

    def format_summary(self) -> str:
        """Format report summary for console.

        Returns:
            Human-readable summary with counts and status
        """
        status = "✅ PASSING" if self.is_passing() else "❌ FAILING"

        summary = f"""
Analysis Report {self.report_id}
Status: {status}
Timestamp: {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
Pitch Deck Version: v{self.pitch_deck_version}
Constitutions Analyzed: {self.constitutions_analyzed}

Issues Found:
  - Errors: {len(self.errors)}
  - Warnings: {len(self.warnings)}
  - Info: {len(self.info)}
"""

        if self.errors:
            summary += "\n[ERRORS]\n"
            for error in self.errors:
                summary += f"  {error.format()}\n"
                if error.suggestion:
                    summary += f"    Suggestion: {error.suggestion}\n"

        if self.warnings:
            summary += "\n[WARNINGS]\n"
            for warning in self.warnings:
                summary += f"  {warning.format()}\n"
                if warning.suggestion:
                    summary += f"    Suggestion: {warning.suggestion}\n"

        if self.info:
            summary += "\n[INFO]\n"
            for info_item in self.info:
                summary += f"  {info_item.format()}\n"

        return summary

    def save_to_changelog(self, changelog_dir: Path) -> Path:
        """Save report to changelog directory.

        Args:
            changelog_dir: Path to .specify/changelog/

        Returns:
            Path to saved report file
        """
        changelog_dir.mkdir(parents=True, exist_ok=True)

        timestamp_str = self.timestamp.strftime("%Y-%m-%d")
        report_file = changelog_dir / f"{timestamp_str}-analyze-report.md"

        content = f"""# Analysis Report

**Report ID**: {self.report_id}
**Date**: {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}
**Pitch Deck Version**: v{self.pitch_deck_version}
**Constitutions Analyzed**: {self.constitutions_analyzed}
**Status**: {"✅ PASSING" if self.is_passing() else "❌ FAILING"}

## Summary

- **Errors**: {len(self.errors)} (blocking issues)
- **Warnings**: {len(self.warnings)} (non-blocking issues)
- **Info**: {len(self.info)} (informational)

"""

        if self.errors:
            content += "## Errors\n\n"
            for i, error in enumerate(self.errors, 1):
                content += f"{i}. {error.format()}\n"
                if error.suggestion:
                    content += f"   - **Suggestion**: {error.suggestion}\n"
                content += "\n"

        if self.warnings:
            content += "## Warnings\n\n"
            for i, warning in enumerate(self.warnings, 1):
                content += f"{i}. {warning.format()}\n"
                if warning.suggestion:
                    content += f"   - **Suggestion**: {warning.suggestion}\n"
                content += "\n"

        if self.info:
            content += "## Informational\n\n"
            for i, info_item in enumerate(self.info, 1):
                content += f"{i}. {info_item.format()}\n"
                content += "\n"

        content += """
## Next Steps

"""

        if self.has_errors():
            content += "- Fix all errors before proceeding\n"
            content += "- Re-run `/bp.analyze` to validate fixes\n"
        else:
            content += "- ✅ All validations passed\n"
            content += "- Ready to run `/bp.checklist` to generate quality gates\n"
            content += "- Or proceed directly to `/speckit.implement`\n"

        report_file.write_text(content, encoding="utf-8")
        return report_file

    def __repr__(self) -> str:
        status = "PASSING" if self.is_passing() else "FAILING"
        return (
            f"AnalysisReport(id='{self.report_id}', status={status}, "
            f"errors={len(self.errors)}, warnings={len(self.warnings)})"
        )
