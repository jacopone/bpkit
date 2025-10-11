"""Git repository model for .gitignore handling."""

from pathlib import Path

from pydantic import BaseModel, Field


class GitRepository(BaseModel):
    """Represents Git repository state for .gitignore handling.

    Attributes:
        exists: True if .git/ directory detected
        gitignore_path: Path to .gitignore file (may not exist)
        gitignore_exists: True if .gitignore file exists
        has_bpkit_entry: True if .gitignore contains BP-Kit entry
    """

    exists: bool = False
    gitignore_path: Path = Field(default=Path(".gitignore"))
    gitignore_exists: bool = False
    has_bpkit_entry: bool = False

    @classmethod
    def detect(cls, project_dir: Path) -> "GitRepository":
        """Detect Git repository state in project directory.

        Args:
            project_dir: Project root directory

        Returns:
            GitRepository instance with detected state
        """
        git_dir = project_dir / ".git"
        gitignore_path = project_dir / ".gitignore"

        instance = cls(
            exists=git_dir.exists(),
            gitignore_path=Path(".gitignore"),
            gitignore_exists=gitignore_path.exists(),
        )

        # Check if .gitignore has BP-Kit entry
        if instance.gitignore_exists:
            content = gitignore_path.read_text()
            instance.has_bpkit_entry = ".specify/deck/*.pdf" in content

        return instance

    def needs_gitignore_prompt(self) -> bool:
        """Check if user should be prompted to create .gitignore.

        Returns:
            True if Git not detected (should prompt user)
        """
        return not self.exists

    def needs_gitignore_entry(self) -> bool:
        """Check if .gitignore needs BP-Kit entry.

        Returns:
            True if .gitignore exists but doesn't have BP-Kit entry
        """
        return self.gitignore_exists and not self.has_bpkit_entry

    def should_create_gitignore(self) -> bool:
        """Check if .gitignore file should be created.

        Returns:
            True if .gitignore doesn't exist
        """
        return not self.gitignore_exists
