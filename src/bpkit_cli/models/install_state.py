"""Installation state model for BP-Kit installation tracking."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


class InstallationStatus(str, Enum):
    """Status of BP-Kit installation."""

    UNINSTALLED = "uninstalled"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"


class InstallationState(BaseModel):
    """Tracks the overall state of BP-Kit installation.

    Used for rollback coordination and validation.

    Attributes:
        status: Current installation status
        project_dir: Project root directory (default: current working directory)
        is_speckit_project: True if .specify/ existed before init
        files_created: Files created during this installation (for rollback)
        dirs_created: Directories created during this installation (for rollback)
        conflicts: List of conflicts detected with Speckit files
        error_message: Error details if status=FAILED
        installed_at: Timestamp when installation completed
    """

    status: InstallationStatus = InstallationStatus.UNINSTALLED
    project_dir: Path = Field(default_factory=Path.cwd)
    is_speckit_project: bool = False
    files_created: List[Path] = Field(default_factory=list)
    dirs_created: List[Path] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    installed_at: Optional[datetime] = None

    def has_conflicts(self) -> bool:
        """Check if there are any installation conflicts.

        Returns:
            True if conflicts detected
        """
        return len(self.conflicts) > 0

    def can_proceed(self) -> bool:
        """Check if installation can proceed.

        Returns:
            True if no conflicts and status allows installation
        """
        return not self.has_conflicts() and self.status in (
            InstallationStatus.UNINSTALLED,
            InstallationStatus.FAILED,
        )

    def mark_installing(self) -> None:
        """Transition to INSTALLING status."""
        if self.status not in (InstallationStatus.UNINSTALLED, InstallationStatus.FAILED):
            raise ValueError(f"Cannot transition to INSTALLING from {self.status}")
        self.status = InstallationStatus.INSTALLING
        self.error_message = None

    def mark_installed(self) -> None:
        """Transition to INSTALLED status."""
        if self.status != InstallationStatus.INSTALLING:
            raise ValueError(f"Cannot transition to INSTALLED from {self.status}")
        self.status = InstallationStatus.INSTALLED
        self.installed_at = datetime.now()

    def mark_failed(self, error: str) -> None:
        """Transition to FAILED status with error message.

        Args:
            error: Error message describing the failure
        """
        self.status = InstallationStatus.FAILED
        self.error_message = error

    def add_created_file(self, file_path: Path) -> None:
        """Track a file created during installation.

        Args:
            file_path: Path to file that was created
        """
        if file_path not in self.files_created:
            self.files_created.append(file_path)

    def add_created_dir(self, dir_path: Path) -> None:
        """Track a directory created during installation.

        Args:
            dir_path: Path to directory that was created
        """
        if dir_path not in self.dirs_created:
            self.dirs_created.append(dir_path)

    def add_conflict(self, conflict: str) -> None:
        """Add a conflict to the list.

        Args:
            conflict: Description of the conflict
        """
        if conflict not in self.conflicts:
            self.conflicts.append(conflict)

    def get_total_files_created(self) -> int:
        """Get total number of files and directories created.

        Returns:
            Total count of files + directories
        """
        return len(self.files_created) + len(self.dirs_created)
