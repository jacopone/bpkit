"""Unit tests for installer module - rollback mechanism."""

import tempfile
from pathlib import Path

import pytest

from bpkit_cli.core.installer import (
    InstallationError,
    InstallationRollback,
    atomic_installation,
)


class TestInstallationRollback:
    """Test the InstallationRollback class."""

    def test_track_file(self, tmp_path: Path):
        """Test file tracking."""
        tracker = InstallationRollback()
        file_path = tmp_path / "test.txt"

        tracker.track_file(file_path)

        assert file_path in tracker.created_files
        assert len(tracker.created_files) == 1

    def test_track_file_existing_not_tracked(self, tmp_path: Path):
        """Test that existing files are not tracked."""
        tracker = InstallationRollback()
        file_path = tmp_path / "existing.txt"
        file_path.write_text("existing")

        tracker.track_file(file_path)

        assert file_path not in tracker.created_files
        assert len(tracker.created_files) == 0

    def test_track_dir(self, tmp_path: Path):
        """Test directory tracking."""
        tracker = InstallationRollback()
        dir_path = tmp_path / "test_dir"

        tracker.track_dir(dir_path)

        assert dir_path in tracker.created_dirs
        assert len(tracker.created_dirs) == 1

    def test_track_dir_existing_not_tracked(self, tmp_path: Path):
        """Test that existing directories are not tracked."""
        tracker = InstallationRollback()
        dir_path = tmp_path / "existing_dir"
        dir_path.mkdir()

        tracker.track_dir(dir_path)

        assert dir_path not in tracker.created_dirs
        assert len(tracker.created_dirs) == 0

    def test_rollback_files_lifo_order(self, tmp_path: Path):
        """Test that files are deleted in LIFO (last in, first out) order."""
        tracker = InstallationRollback()

        # Create files in order
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file3 = tmp_path / "file3.txt"

        tracker.track_file(file1)
        file1.write_text("content1")

        tracker.track_file(file2)
        file2.write_text("content2")

        tracker.track_file(file3)
        file3.write_text("content3")

        # Rollback
        tracker.rollback()

        # All files should be deleted
        assert not file1.exists()
        assert not file2.exists()
        assert not file3.exists()

    def test_rollback_directories_lifo_order(self, tmp_path: Path):
        """Test that directories are deleted in LIFO order."""
        tracker = InstallationRollback()

        # Create nested directories
        dir1 = tmp_path / "dir1"
        dir2 = dir1 / "dir2"
        dir3 = dir2 / "dir3"

        tracker.track_dir(dir1)
        dir1.mkdir()

        tracker.track_dir(dir2)
        dir2.mkdir()

        tracker.track_dir(dir3)
        dir3.mkdir()

        # Rollback
        tracker.rollback()

        # All empty directories should be deleted (LIFO order ensures nested are deleted first)
        assert not dir3.exists()
        assert not dir2.exists()
        assert not dir1.exists()

    def test_rollback_only_deletes_created_paths(self, tmp_path: Path):
        """Test that rollback only deletes paths it created, not pre-existing ones."""
        tracker = InstallationRollback()

        # Pre-existing file
        existing_file = tmp_path / "existing.txt"
        existing_file.write_text("existing content")

        # New file
        new_file = tmp_path / "new.txt"
        tracker.track_file(new_file)
        new_file.write_text("new content")

        # Rollback
        tracker.rollback()

        # Pre-existing file should remain
        assert existing_file.exists()
        assert existing_file.read_text() == "existing content"

        # New file should be deleted
        assert not new_file.exists()

    def test_rollback_skips_nonexistent_files(self, tmp_path: Path):
        """Test that rollback handles files that don't exist gracefully."""
        tracker = InstallationRollback()

        # Track a file but don't create it
        phantom_file = tmp_path / "phantom.txt"
        tracker.track_file(phantom_file)

        # Rollback should not raise an error
        tracker.rollback()  # Should succeed without exception

    def test_rollback_skips_nonempty_directories(self, tmp_path: Path):
        """Test that rollback doesn't delete non-empty directories."""
        tracker = InstallationRollback()

        # Create directory
        dir_path = tmp_path / "dir_with_content"
        tracker.track_dir(dir_path)
        dir_path.mkdir()

        # Add untracked file (simulates user adding content)
        untracked_file = dir_path / "user_file.txt"
        untracked_file.write_text("user content")

        # Rollback
        tracker.rollback()

        # Directory should still exist (not empty)
        assert dir_path.exists()
        assert untracked_file.exists()

    def test_rollback_partial_state_cleanup(self, tmp_path: Path):
        """Test rollback cleans up partial installation state."""
        tracker = InstallationRollback()

        # Simulate partial installation
        dir1 = tmp_path / "dir1"
        tracker.track_dir(dir1)
        dir1.mkdir()

        file1 = dir1 / "file1.txt"
        tracker.track_file(file1)
        file1.write_text("content")

        dir2 = tmp_path / "dir2"
        tracker.track_dir(dir2)
        dir2.mkdir()

        file2 = dir2 / "file2.txt"
        tracker.track_file(file2)
        file2.write_text("content")

        # Rollback
        tracker.rollback()

        # All should be cleaned up
        assert not file1.exists()
        assert not file2.exists()
        assert not dir1.exists()
        assert not dir2.exists()


class TestAtomicInstallation:
    """Test the atomic_installation context manager."""

    def test_atomic_installation_success(self, tmp_path: Path):
        """Test successful installation doesn't trigger rollback."""
        test_file = tmp_path / "test.txt"

        with atomic_installation() as tracker:
            tracker.track_file(test_file)
            test_file.write_text("content")

        # File should still exist after context exit
        assert test_file.exists()

    def test_atomic_installation_raises_installation_error_on_exception(self, tmp_path: Path):
        """Test that exceptions trigger rollback and raise InstallationError."""
        test_file = tmp_path / "test.txt"

        with pytest.raises(InstallationError) as exc_info:
            with atomic_installation() as tracker:
                tracker.track_file(test_file)
                test_file.write_text("content")
                raise ValueError("Simulated failure")

        # File should be rolled back
        assert not test_file.exists()

        # Should raise InstallationError with original exception chained
        assert "Installation failed" in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, ValueError)

    def test_atomic_installation_rollback_on_failure(self, tmp_path: Path):
        """Test that rollback happens on any exception."""
        dir1 = tmp_path / "dir1"
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"

        with pytest.raises(InstallationError):
            with atomic_installation() as tracker:
                # Create some resources
                tracker.track_dir(dir1)
                dir1.mkdir()

                tracker.track_file(file1)
                file1.write_text("content1")

                tracker.track_file(file2)
                file2.write_text("content2")

                # Simulate failure
                raise RuntimeError("Installation failed midway")

        # All resources should be rolled back
        assert not dir1.exists()
        assert not file1.exists()
        assert not file2.exists()

    def test_atomic_installation_preserves_existing_files(self, tmp_path: Path):
        """Test that existing files are preserved during rollback."""
        existing_file = tmp_path / "existing.txt"
        existing_file.write_text("existing content")

        new_file = tmp_path / "new.txt"

        with pytest.raises(InstallationError):
            with atomic_installation() as tracker:
                tracker.track_file(new_file)
                new_file.write_text("new content")
                raise RuntimeError("Failure")

        # Existing file should remain untouched
        assert existing_file.exists()
        assert existing_file.read_text() == "existing content"

        # New file should be deleted
        assert not new_file.exists()
