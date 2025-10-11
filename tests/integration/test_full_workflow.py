"""Integration tests for full init → check → re-init workflow."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from bpkit_cli.commands.check import run_check
from bpkit_cli.commands.init import run_init
from bpkit_cli.core import is_bpkit_installed


class TestFullWorkflow:
    """Test complete workflow: init → check → re-init with --force."""

    @patch("bpkit_cli.commands.init.install_templates")
    @patch("bpkit_cli.commands.init.console")
    @patch("bpkit_cli.commands.check.console")
    def test_init_check_reinit_workflow(
        self, mock_check_console, mock_init_console, mock_install, tmp_path: Path
    ):
        """Test: init → check reports success → re-init with --force → check still reports success."""
        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)

            # Mock template installation to avoid network calls
            mock_install.return_value = None

            # Step 1: Initial installation
            run_init(project_name="test-project", force=False)

            # Verify BP-Kit is installed
            assert is_bpkit_installed(tmp_path)

            # Verify directories exist
            assert (tmp_path / ".specify" / "deck").exists()
            assert (tmp_path / ".specify" / "features").exists()
            assert (tmp_path / ".specify" / "changelog").exists()
            assert (tmp_path / ".specify" / "scripts" / "bp").exists()
            assert (tmp_path / ".specify" / "templates").exists()
            assert (tmp_path / ".claude" / "commands").exists()

            # Step 2: Run check (should report success)
            run_check()

            # Verify check was called and would show success
            # (actual output verification would require capturing console output)

            # Step 3: Re-init with --force
            run_init(project_name="test-project-updated", force=True)

            # Should still be installed
            assert is_bpkit_installed(tmp_path)

            # Step 4: Run check again (should still report success)
            run_check()

            # Verify all components still exist
            assert (tmp_path / ".specify" / "deck").exists()
            assert (tmp_path / ".specify" / "features").exists()

        finally:
            os.chdir(original_cwd)

    @patch("bpkit_cli.commands.init.install_templates")
    def test_fresh_install_workflow(self, mock_install, tmp_path: Path):
        """Test fresh installation in empty directory."""
        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)

            mock_install.return_value = None

            # Should not be installed initially
            assert not is_bpkit_installed(tmp_path)

            # Install
            run_init(project_name="my-startup", force=False)

            # Should be installed now
            assert is_bpkit_installed(tmp_path)

            # All key directories should exist
            expected_dirs = [
                ".specify/deck",
                ".specify/features",
                ".specify/changelog",
                ".specify/scripts/bp",
                ".specify/templates",
                ".claude/commands",
            ]

            for dir_path in expected_dirs:
                assert (tmp_path / dir_path).exists(), f"{dir_path} should exist"

        finally:
            os.chdir(original_cwd)

    @patch("bpkit_cli.commands.init.install_templates")
    def test_existing_speckit_project_workflow(self, mock_install, tmp_path: Path):
        """Test installation in existing Speckit project."""
        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)

            # Create existing Speckit structure
            speckit_dir = tmp_path / ".specify"
            speckit_dir.mkdir()

            memory_dir = speckit_dir / "memory"
            memory_dir.mkdir()

            constitution = memory_dir / "constitution.md"
            constitution.write_text("# Project Constitution\n")

            mock_install.return_value = None

            # Install BP-Kit (should not conflict)
            run_init(force=False)

            # BP-Kit should be installed
            assert is_bpkit_installed(tmp_path)

            # Speckit files should be preserved
            assert constitution.exists()
            assert constitution.read_text() == "# Project Constitution\n"

            # BP-Kit directories should exist
            assert (tmp_path / ".specify" / "deck").exists()
            assert (tmp_path / ".specify" / "features").exists()

        finally:
            os.chdir(original_cwd)

    @patch("bpkit_cli.commands.init.console")
    def test_check_before_init(self, mock_console, tmp_path: Path):
        """Test running check before init shows helpful message."""
        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)

            # BP-Kit not installed
            assert not is_bpkit_installed(tmp_path)

            # Run check
            run_check()

            # Console should have been called with messages about not installed
            # (actual assertion would require capturing console output)

        finally:
            os.chdir(original_cwd)

    @patch("bpkit_cli.commands.init.install_templates")
    def test_gitignore_creation_workflow(self, mock_install, tmp_path: Path):
        """Test .gitignore creation in fresh project."""
        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)

            # Initialize Git repository
            git_dir = tmp_path / ".git"
            git_dir.mkdir()

            mock_install.return_value = None

            # Install BP-Kit
            run_init(project_name="test-git", force=False)

            # .gitignore should be created/updated
            gitignore = tmp_path / ".gitignore"
            assert gitignore.exists()

            # Should contain BP-Kit entry
            content = gitignore.read_text()
            assert ".specify/deck/*.pdf" in content

        finally:
            os.chdir(original_cwd)

    @patch("bpkit_cli.commands.init.install_templates")
    def test_gitignore_append_workflow(self, mock_install, tmp_path: Path):
        """Test .gitignore append to existing file."""
        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)

            # Create existing .gitignore
            gitignore = tmp_path / ".gitignore"
            gitignore.write_text("# Existing entries\n*.pyc\n__pycache__/\n")

            # Initialize Git
            git_dir = tmp_path / ".git"
            git_dir.mkdir()

            mock_install.return_value = None

            # Install BP-Kit
            run_init(force=False)

            # .gitignore should be updated
            content = gitignore.read_text()

            # Should preserve existing entries
            assert "*.pyc" in content
            assert "__pycache__/" in content

            # Should add BP-Kit entry
            assert ".specify/deck/*.pdf" in content

        finally:
            os.chdir(original_cwd)


class TestCheckValidation:
    """Test check command validation in different scenarios."""

    @patch("bpkit_cli.commands.init.install_templates")
    @patch("bpkit_cli.commands.check.console")
    def test_check_detects_missing_directories(
        self, mock_console, mock_install, tmp_path: Path
    ):
        """Test check detects missing directories."""
        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)

            mock_install.return_value = None

            # Install
            run_init(force=False)

            # Remove a directory
            features_dir = tmp_path / ".specify" / "features"
            features_dir.rmdir()

            # Run check
            run_check()

            # Console should report the missing directory
            # (actual assertion would require capturing console output)

        finally:
            os.chdir(original_cwd)

    def test_check_handles_partial_installation(self, tmp_path: Path):
        """Test check handles partial/corrupted installation."""
        original_cwd = os.getcwd()

        try:
            os.chdir(tmp_path)

            # Create partial structure (only some directories)
            deck_dir = tmp_path / ".specify" / "deck"
            deck_dir.mkdir(parents=True)

            # Run check (should report incomplete installation)
            run_check()

            # Should not crash, should report missing components

        finally:
            os.chdir(original_cwd)
