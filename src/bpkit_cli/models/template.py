"""Template model for BP-Kit template files."""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, HttpUrl, field_validator


class TemplateType(str, Enum):
    """Type of template file."""

    MARKDOWN = "markdown"
    BASH_SCRIPT = "bash"
    SLASH_COMMAND = "command"


class Template(BaseModel):
    """Represents a BP-Kit template file.

    Attributes:
        name: Template filename (e.g., "pitch-deck-template.md")
        source_url: GitHub raw content URL
        destination_path: Where to install relative to project root
        content: Template file content (None until downloaded)
        type: Type of template (markdown, bash, or slash command)
        size_bytes: Content size for validation (optional)
    """

    name: str
    source_url: HttpUrl
    destination_path: Path
    content: Optional[str] = None
    type: TemplateType
    size_bytes: Optional[int] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate template filename has correct extension.

        Args:
            v: Filename to validate

        Returns:
            Validated filename

        Raises:
            ValueError: If filename doesn't end with .md or .sh
        """
        if not (v.endswith(".md") or v.endswith(".sh")):
            raise ValueError(f"Template name must end with .md or .sh, got: {v}")
        return v

    @field_validator("destination_path")
    @classmethod
    def validate_destination(cls, v: Path) -> Path:
        """Validate destination path is within allowed directories.

        Args:
            v: Destination path to validate

        Returns:
            Validated path

        Raises:
            ValueError: If path is not within .specify/ or .claude/commands/
        """
        path_str = str(v)
        if not (path_str.startswith(".specify/") or path_str.startswith(".claude/commands/")):
            raise ValueError(
                f"Destination must be within .specify/ or .claude/commands/, got: {v}"
            )
        return v

    @field_validator("size_bytes")
    @classmethod
    def validate_size(cls, v: Optional[int]) -> Optional[int]:
        """Validate template size is under 1MB limit.

        Args:
            v: Size in bytes

        Returns:
            Validated size

        Raises:
            ValueError: If size exceeds 1MB
        """
        if v is not None and v > 1024 * 1024:  # 1MB
            raise ValueError(f"Template size must be < 1MB, got: {v} bytes")
        return v

    def is_downloaded(self) -> bool:
        """Check if template content has been downloaded.

        Returns:
            True if content is populated, False otherwise
        """
        return self.content is not None

    def get_file_extension(self) -> str:
        """Get the file extension.

        Returns:
            File extension including dot (e.g., ".md", ".sh")
        """
        return Path(self.name).suffix
