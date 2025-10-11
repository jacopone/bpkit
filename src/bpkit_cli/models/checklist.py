"""Checklist models for BP-Kit quality commands."""

from datetime import datetime
from pathlib import Path
from typing import Any

from ..models.constitution import ConstitutionType


class ChecklistItem:
    """Individual validation criterion in a quality checklist."""

    def __init__(
        self,
        item_id: str,
        description: str,
        is_checked: bool = False,
        category: str = "General",
    ) -> None:
        """Initialize checklist item.

        Args:
            item_id: Unique item ID (CHK001, CHK002, etc.)
            description: Validation criterion description
            is_checked: Whether item has been checked by user
            category: Category (Traceability, Quality, Completeness)
        """
        self.item_id = item_id
        self.description = description
        self.is_checked = is_checked
        self.category = category

    def to_markdown(self) -> str:
        """Convert to markdown checkbox format.

        Returns:
            Markdown checkbox string

        Example:
            >>> item = ChecklistItem("CHK001", "All principles have measurable outcomes")
            >>> item.to_markdown()
            '- [ ] All principles have measurable outcomes'
            >>> item.check()
            >>> item.to_markdown()
            '- [x] All principles have measurable outcomes'
        """
        checkbox = "[x]" if self.is_checked else "[ ]"
        return f"- {checkbox} {self.description}"

    def check(self) -> None:
        """Mark item as checked."""
        self.is_checked = True

    def uncheck(self) -> None:
        """Mark item as unchecked."""
        self.is_checked = False

    def __repr__(self) -> str:
        status = "checked" if self.is_checked else "unchecked"
        return f"ChecklistItem(id='{self.item_id}', status={status})"


class Checklist:
    """Collection of checklist items for a constitution."""

    def __init__(
        self,
        checklist_id: str,
        constitution_file: Path,
        constitution_type: ConstitutionType,
        items: list[ChecklistItem] | None = None,
        last_updated: datetime | None = None,
    ) -> None:
        """Initialize checklist.

        Args:
            checklist_id: Unique checklist ID
            constitution_file: Path to target constitution
            constitution_type: STRATEGIC or FEATURE
            items: List of ChecklistItem objects
            last_updated: Last update timestamp
        """
        self.checklist_id = checklist_id
        self.constitution_file = constitution_file
        self.constitution_type = constitution_type
        self.items = items or []
        self.last_updated = last_updated or datetime.now()

    def add_item(self, item: ChecklistItem) -> None:
        """Add item to checklist.

        Args:
            item: ChecklistItem to add
        """
        self.items.append(item)

    def calculate_completion(self) -> float:
        """Calculate completion percentage.

        Returns:
            Percentage of checked items (0.0 to 100.0)

        Example:
            >>> checklist = Checklist("CL001", Path("file.md"), ConstitutionType.STRATEGIC)
            >>> checklist.add_item(ChecklistItem("1", "Item 1", is_checked=True))
            >>> checklist.add_item(ChecklistItem("2", "Item 2", is_checked=False))
            >>> checklist.calculate_completion()
            50.0
        """
        if not self.items:
            return 0.0

        checked_count = sum(1 for item in self.items if item.is_checked)
        return (checked_count / len(self.items)) * 100.0

    @classmethod
    def parse_from_file(cls, path: Path) -> "Checklist":
        """Parse checklist from existing markdown file.

        Args:
            path: Path to checklist markdown file

        Returns:
            Checklist instance

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file format is invalid

        Example:
            >>> checklist = Checklist.parse_from_file(Path(".specify/checklists/company.md"))
            >>> checklist.calculate_completion()
            80.0
        """
        if not path.exists():
            raise FileNotFoundError(f"Checklist file not found: {path}")

        content = path.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Extract metadata from frontmatter or header
        checklist_id = f"CL-{path.stem}"
        constitution_file = Path("")  # Will be parsed from content
        constitution_type = ConstitutionType.STRATEGIC  # Default
        items: list[ChecklistItem] = []

        # Parse markdown checkboxes
        item_counter = 1
        current_category = "General"

        for line in lines:
            # Check for category headers (## Traceability, ## Quality, etc.)
            if line.startswith("## "):
                current_category = line[3:].strip()
                continue

            # Check for checklist items (- [ ] or - [x])
            if line.strip().startswith("- ["):
                # Extract checkbox state
                is_checked = "[x]" in line.lower() or "[X]" in line.lower()

                # Extract description (everything after checkbox)
                if "- [ ]" in line:
                    description = line.split("- [ ]", 1)[1].strip()
                elif "- [x]" in line.lower():
                    # Handle both [x] and [X]
                    description = line.split("]", 1)[1].strip()
                else:
                    continue

                item = ChecklistItem(
                    item_id=f"CHK{item_counter:03d}",
                    description=description,
                    is_checked=is_checked,
                    category=current_category,
                )
                items.append(item)
                item_counter += 1

            # Extract constitution reference
            if "**Constitution**:" in line:
                # Format: **Constitution**: [filename](../path/to/file.md)
                import re

                match = re.search(r"\((.*?\.md)\)", line)
                if match:
                    constitution_file = Path(match.group(1))

            # Extract constitution type
            if "**Type**:" in line:
                if "Strategic" in line:
                    constitution_type = ConstitutionType.STRATEGIC
                elif "Feature" in line:
                    constitution_type = ConstitutionType.FEATURE

        # Get last modified time
        try:
            last_updated = datetime.fromtimestamp(path.stat().st_mtime)
        except Exception:
            last_updated = datetime.now()

        return cls(
            checklist_id=checklist_id,
            constitution_file=constitution_file,
            constitution_type=constitution_type,
            items=items,
            last_updated=last_updated,
        )

    def save_to_file(self, path: Path) -> None:
        """Save checklist to markdown file.

        Args:
            path: Path where checklist should be saved

        Raises:
            IOError: If file cannot be written

        Example:
            >>> checklist = Checklist("CL001", Path("company.md"), ConstitutionType.STRATEGIC)
            >>> checklist.add_item(ChecklistItem("1", "Item 1"))
            >>> checklist.save_to_file(Path(".specify/checklists/company.md"))
        """
        # Create directory if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        # Build content
        content = f"""# Quality Checklist: {self.constitution_file.stem}

**Constitution**: [{self.constitution_file.name}](../memory/{self.constitution_file.name if self.constitution_type == ConstitutionType.STRATEGIC else f'../features/{self.constitution_file.name}'})
**Type**: {self.constitution_type.value.capitalize()}
**Generated**: {self.last_updated.strftime("%Y-%m-%d")}
**Completion**: {self.calculate_completion():.0f}%

"""

        # Group items by category
        categories: dict[str, list[ChecklistItem]] = {}
        for item in self.items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)

        # Write items by category
        for category, category_items in categories.items():
            content += f"## {category} ({len(category_items)} items)\n\n"
            for item in category_items:
                content += f"{item.to_markdown()}\n"
            content += "\n"

        # Add footer
        completion = self.calculate_completion()
        if completion == 100.0:
            content += "---\n\n✅ **All items completed!** Ready for implementation.\n"
        else:
            remaining = len([i for i in self.items if not i.is_checked])
            content += f"---\n\n**Progress**: {completion:.0f}% complete ({remaining} items remaining)\n"

        # Write to file
        try:
            path.write_text(content, encoding="utf-8")
        except Exception as e:
            raise IOError(f"Failed to write checklist to {path}: {e}") from e

    def __repr__(self) -> str:
        completion = self.calculate_completion()
        return (
            f"Checklist(id='{self.checklist_id}', type={self.constitution_type.value}, "
            f"items={len(self.items)}, completion={completion:.0f}%)"
        )
