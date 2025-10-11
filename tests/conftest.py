"""Pytest configuration and fixtures for BP-Kit tests."""

import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import Mock

import pytest
from httpx import Response


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing.

    Yields:
        Path to temporary directory that will be cleaned up after test.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def speckit_project(temp_dir: Path) -> Path:
    """Create a mock Speckit project structure.

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path to project root with .specify/ directory
    """
    specify_dir = temp_dir / ".specify"
    specify_dir.mkdir()

    # Create some existing Speckit files
    (specify_dir / "memory").mkdir()
    (specify_dir / "memory" / "constitution.md").write_text("# Speckit Constitution\n")

    (specify_dir / "templates").mkdir()
    (specify_dir / "templates" / "spec-template.md").write_text("# Spec Template\n")

    return temp_dir


@pytest.fixture
def empty_project(temp_dir: Path) -> Path:
    """Create an empty project directory (no Speckit).

    Args:
        temp_dir: Temporary directory fixture

    Returns:
        Path to empty project root
    """
    return temp_dir


@pytest.fixture
def mock_httpx_response() -> Mock:
    """Create a mock httpx Response for template downloads.

    Returns:
        Mock Response object with successful status
    """
    response = Mock(spec=Response)
    response.status_code = 200
    response.text = "# Mock Template Content\n\nProject: [PROJECT_NAME]\n"
    response.raise_for_status = Mock()
    return response


@pytest.fixture
def mock_template_content() -> str:
    """Standard mock template content for testing.

    Returns:
        Template content with [PROJECT_NAME] placeholder
    """
    return """# Pitch Deck Template

## Company Purpose

Project: [PROJECT_NAME]

Mission: Transform business plans into executable specifications.
"""


@pytest.fixture
def bpkit_project(speckit_project: Path) -> Path:
    """Create a project with BP-Kit already installed.

    Args:
        speckit_project: Speckit project fixture

    Returns:
        Path to project with BP-Kit installed
    """
    specify_dir = speckit_project / ".specify"

    # Create BP-Kit directories
    (specify_dir / "deck").mkdir()
    (specify_dir / "features").mkdir()
    (specify_dir / "changelog").mkdir()
    (specify_dir / "scripts" / "bp").mkdir(parents=True)

    # Create BP-Kit templates
    (specify_dir / "templates" / "pitch-deck-template.md").write_text("# Pitch Deck\n")
    (specify_dir / "templates" / "strategic-constitution-template.md").write_text(
        "# Strategic Constitution\n"
    )
    (specify_dir / "templates" / "feature-constitution-template.md").write_text(
        "# Feature Constitution\n"
    )

    # Create slash commands
    claude_dir = speckit_project / ".claude" / "commands"
    claude_dir.mkdir(parents=True)
    (claude_dir / "bp.decompose.md").write_text("# Decompose Command\n")
    (claude_dir / "bp.sync.md").write_text("# Sync Command\n")

    # Create bash scripts
    scripts_dir = specify_dir / "scripts" / "bp"
    (scripts_dir / "bp-common.sh").write_text("#!/bin/bash\n")
    (scripts_dir / "decompose-setup.sh").write_text("#!/bin/bash\n")

    return speckit_project
