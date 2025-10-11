"""Version tracking utilities for BP-Kit documents."""

import re
from enum import Enum
from pathlib import Path
from typing import Literal

import yaml


class BumpType(str, Enum):
    """Semantic version bump types."""

    MAJOR = "MAJOR"
    MINOR = "MINOR"
    PATCH = "PATCH"


class VersionTracker:
    """Track and manage semantic versions in markdown documents."""

    VERSION_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

    @staticmethod
    def parse_version(version_str: str) -> tuple[int, int, int]:
        """Parse semantic version string into (major, minor, patch) tuple.

        Args:
            version_str: Version string in format "X.Y.Z"

        Returns:
            Tuple of (major, minor, patch) integers

        Raises:
            ValueError: If version string is not valid semantic version

        Example:
            >>> VersionTracker.parse_version("1.2.3")
            (1, 2, 3)
            >>> VersionTracker.parse_version("invalid")
            Traceback (most recent call last):
            ...
            ValueError: Invalid semantic version: invalid
        """
        match = VersionTracker.VERSION_PATTERN.match(version_str)
        if not match:
            raise ValueError(f"Invalid semantic version: {version_str}")

        major, minor, patch = match.groups()
        return (int(major), int(minor), int(patch))

    @staticmethod
    def compare_versions(version1: str, version2: str) -> Literal[-1, 0, 1]:
        """Compare two semantic versions.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            -1 if version1 < version2
            0 if version1 == version2
            1 if version1 > version2

        Raises:
            ValueError: If either version string is invalid

        Example:
            >>> VersionTracker.compare_versions("1.0.0", "1.0.1")
            -1
            >>> VersionTracker.compare_versions("2.0.0", "1.9.9")
            1
            >>> VersionTracker.compare_versions("1.2.3", "1.2.3")
            0
        """
        v1_parts = VersionTracker.parse_version(version1)
        v2_parts = VersionTracker.parse_version(version2)

        if v1_parts < v2_parts:
            return -1
        elif v1_parts > v2_parts:
            return 1
        else:
            return 0

    @staticmethod
    def bump_version(current_version: str, bump_type: BumpType) -> str:
        """Bump semantic version according to bump type.

        Args:
            current_version: Current version string
            bump_type: Type of bump (MAJOR, MINOR, or PATCH)

        Returns:
            New version string after bump

        Raises:
            ValueError: If current version is invalid

        Example:
            >>> VersionTracker.bump_version("1.2.3", BumpType.PATCH)
            '1.2.4'
            >>> VersionTracker.bump_version("1.2.3", BumpType.MINOR)
            '1.3.0'
            >>> VersionTracker.bump_version("1.2.3", BumpType.MAJOR)
            '2.0.0'
        """
        major, minor, patch = VersionTracker.parse_version(current_version)

        if bump_type == BumpType.MAJOR:
            return f"{major + 1}.0.0"
        elif bump_type == BumpType.MINOR:
            return f"{major}.{minor + 1}.0"
        elif bump_type == BumpType.PATCH:
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

    @staticmethod
    def extract_version_from_frontmatter(file_path: Path) -> str | None:
        """Extract version from YAML frontmatter in markdown file.

        Looks for 'version' field in frontmatter between --- delimiters.

        Args:
            file_path: Path to markdown file

        Returns:
            Version string if found, None otherwise

        Example:
            Given file with frontmatter:
            ---
            version: 1.2.3
            ---
            # Content

            >>> VersionTracker.extract_version_from_frontmatter(Path("file.md"))
            '1.2.3'
        """
        if not file_path.exists():
            return None

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return None

        # Check if file starts with frontmatter delimiter
        if not content.startswith("---\n"):
            return None

        # Find end of frontmatter
        end_delimiter = content.find("\n---\n", 4)
        if end_delimiter == -1:
            # Try alternative ending (--- at start of line)
            end_delimiter = content.find("\n---", 4)
            if end_delimiter == -1:
                return None

        # Extract frontmatter YAML
        frontmatter_content = content[4:end_delimiter]

        try:
            frontmatter = yaml.safe_load(frontmatter_content)
            if isinstance(frontmatter, dict):
                version = frontmatter.get("version")
                if isinstance(version, (str, int, float)):
                    return str(version)
        except yaml.YAMLError:
            return None

        return None

    @staticmethod
    def update_version_in_frontmatter(file_path: Path, new_version: str) -> None:
        """Update version field in YAML frontmatter.

        Args:
            file_path: Path to markdown file
            new_version: New version string to set

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file has no frontmatter or version field

        Example:
            Given file with frontmatter:
            ---
            version: 1.0.0
            ---

            >>> VersionTracker.update_version_in_frontmatter(Path("file.md"), "1.0.1")
            # File now has version: 1.0.1 in frontmatter
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")

        if not content.startswith("---\n"):
            raise ValueError(f"File {file_path} has no YAML frontmatter")

        # Find end of frontmatter
        end_delimiter = content.find("\n---\n", 4)
        if end_delimiter == -1:
            end_delimiter = content.find("\n---", 4)
            if end_delimiter == -1:
                raise ValueError(f"File {file_path} has incomplete YAML frontmatter")

        # Extract and parse frontmatter
        frontmatter_content = content[4:end_delimiter]
        try:
            frontmatter = yaml.safe_load(frontmatter_content)
            if not isinstance(frontmatter, dict):
                raise ValueError(f"File {file_path} frontmatter is not a dictionary")
        except yaml.YAMLError as e:
            raise ValueError(f"File {file_path} has invalid YAML frontmatter: {e}") from e

        # Update version
        if "version" not in frontmatter:
            raise ValueError(f"File {file_path} has no 'version' field in frontmatter")

        frontmatter["version"] = new_version

        # Reconstruct file with updated frontmatter
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        rest_of_content = content[end_delimiter + 5 :]  # +5 for "\n---\n"

        new_content = f"---\n{new_frontmatter}---\n{rest_of_content}"

        file_path.write_text(new_content, encoding="utf-8")
