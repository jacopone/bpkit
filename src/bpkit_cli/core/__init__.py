"""BP-Kit core utilities."""

from .installer import InstallationError, InstallationRollback, atomic_installation
from .templates import TemplateDownloadError, download_template, replace_placeholders
from .validation import (
    check_speckit_conflicts,
    detect_git,
    is_bpkit_installed,
    is_speckit_project,
)

# Quality commands core modules (Feature 002)
# from .markdown_parser import MarkdownParser
# from .version_tracker import VersionTracker
# from .link_validator import LinkValidator
# from .ambiguity_detector import AmbiguityDetector
# from .conflict_detector import ConflictDetector

__all__ = [
    "InstallationError",
    "InstallationRollback",
    "TemplateDownloadError",
    "atomic_installation",
    "download_template",
    "replace_placeholders",
    "check_speckit_conflicts",
    "detect_git",
    "is_bpkit_installed",
    "is_speckit_project",
    # Quality commands core modules (uncomment as implemented)
    # "MarkdownParser",
    # "VersionTracker",
    # "LinkValidator",
    # "AmbiguityDetector",
    # "ConflictDetector",
]
