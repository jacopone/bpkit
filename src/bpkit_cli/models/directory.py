"""Directory model for BP-Kit directory management."""

from pathlib import Path

from pydantic import BaseModel, field_validator


class Directory(BaseModel):
    """Represents a directory to be created during installation.

    Attributes:
        path: Directory path relative to project root
        exists_before_install: True if existed before bpkit init ran
        created_by_bpkit: True if created by current installation
        is_empty: True if directory contains no files
    """

    path: Path
    exists_before_install: bool = False
    created_by_bpkit: bool = False
    is_empty: bool = True

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: Path) -> Path:
        """Validate path is within .specify/ hierarchy.

        Args:
            v: Path to validate

        Returns:
            Validated path

        Raises:
            ValueError: If path is not within .specify/
        """
        path_str = str(v)
        if not path_str.startswith(".specify/"):
            raise ValueError(f"Directory path must be within .specify/, got: {v}")
        return v

    def should_delete_on_rollback(self) -> bool:
        """Determine if this directory should be deleted during rollback.

        Directories are only deleted if:
        - Created by current installation
        - Is empty (safety check)
        - Didn't exist before installation

        Returns:
            True if safe to delete during rollback
        """
        return self.created_by_bpkit and self.is_empty and not self.exists_before_install

    def update_status(self, project_root: Path) -> None:
        """Update directory status based on current filesystem state.

        Args:
            project_root: Project root directory to resolve relative paths
        """
        full_path = project_root / self.path
        self.exists_before_install = full_path.exists()

        if full_path.exists():
            # Check if empty (no files, only .gitkeep or README allowed)
            contents = list(full_path.iterdir())
            self.is_empty = len(contents) == 0 or all(
                f.name in (".gitkeep", "README.md") for f in contents
            )
