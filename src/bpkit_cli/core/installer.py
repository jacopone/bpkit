"""Installation and rollback utilities for BP-Kit."""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List

from rich.console import Console

console = Console()


class InstallationError(Exception):
    """Raised when installation fails."""

    pass


class InstallationRollback:
    """Tracks created files and directories for rollback on failure.

    Implements LIFO (last in, first out) deletion order to safely
    remove created resources if installation fails.
    """

    def __init__(self) -> None:
        """Initialize empty tracking lists."""
        self.created_files: List[Path] = []
        self.created_dirs: List[Path] = []

    def track_file(self, path: Path) -> None:
        """Track a file that will be created.

        Only tracks if file doesn't already exist (new creation).

        Args:
            path: Path to file that will be created
        """
        if not path.exists():
            self.created_files.append(path)

    def track_dir(self, path: Path) -> None:
        """Track a directory that will be created.

        Only tracks if directory doesn't already exist (new creation).

        Args:
            path: Path to directory that will be created
        """
        if not path.exists():
            self.created_dirs.append(path)

    def rollback(self) -> None:
        """Rollback all tracked changes in LIFO order.

        Deletes files first, then directories. Only deletes empty
        directories to prevent accidental data loss.
        """
        console.print("\n[yellow]Rolling back changes...[/yellow]")

        # Delete files in reverse order (LIFO)
        for file_path in reversed(self.created_files):
            if file_path.exists():
                try:
                    file_path.unlink()
                    console.print(f"  [dim]Deleted {file_path}[/dim]")
                except Exception as e:
                    console.print(f"  [yellow]Warning: Could not delete {file_path}: {e}[/yellow]")

        # Delete directories in reverse order (LIFO), only if empty
        for dir_path in reversed(self.created_dirs):
            if dir_path.exists():
                try:
                    # Only remove if directory is empty
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        console.print(f"  [dim]Deleted {dir_path}/[/dim]")
                    else:
                        console.print(
                            f"  [yellow]Skipped {dir_path}/ (not empty)[/yellow]"
                        )
                except Exception as e:
                    console.print(
                        f"  [yellow]Warning: Could not delete {dir_path}: {e}[/yellow]"
                    )

        console.print("[green]✓ Rollback complete[/green]")


@contextmanager
def atomic_installation() -> Generator[InstallationRollback, None, None]:
    """Context manager for atomic installation with automatic rollback.

    If any exception occurs during installation, automatically rolls back
    all tracked changes.

    Yields:
        InstallationRollback instance for tracking created resources

    Raises:
        InstallationError: Re-raises any exception as InstallationError
                          after performing rollback

    Example:
        >>> with atomic_installation() as tracker:
        ...     tracker.track_dir(Path(".specify/deck"))
        ...     Path(".specify/deck").mkdir()
        ...     tracker.track_file(Path(".specify/deck/README.md"))
        ...     Path(".specify/deck/README.md").write_text("# Deck\\n")
        ...     # If any error occurs here, rollback happens automatically
    """
    tracker = InstallationRollback()
    try:
        yield tracker
    except Exception as e:
        tracker.rollback()
        raise InstallationError(f"Installation failed: {e}. All changes rolled back.") from e
