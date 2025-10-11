"""Conflict detection for constitutional principles."""

from pathlib import Path
from typing import Any

from ..core.markdown_parser import MarkdownParser
from ..core.version_tracker import VersionTracker
from ..models.constitution import Constitution
from ..models.pitch_deck import PitchDeck


class ConflictDetector:
    """Detect conflicts and coverage gaps in constitutions."""

    def __init__(self) -> None:
        """Initialize conflict detector."""
        self._parser = MarkdownParser()
        self._version_tracker = VersionTracker()

    def detect_conflicts(self, constitutions: list[Constitution]) -> list[tuple[str, str, str]]:
        """Detect contradictory principles across strategic constitutions.

        This is a simplified implementation that looks for obvious contradictions
        in principle text. A more sophisticated version would use NLP/semantic analysis.

        Args:
            constitutions: List of Constitution objects to analyze

        Returns:
            List of (file1, principle1, file2, principle2, conflict_reason) tuples

        Example:
            >>> detector = ConflictDetector()
            >>> const1 = Constitution.parse(Path(".specify/memory/product.md"))
            >>> const2 = Constitution.parse(Path(".specify/memory/market.md"))
            >>> conflicts = detector.detect_conflicts([const1, const2])
            >>> len(conflicts)
            1
        """
        conflicts: list[tuple[str, str, str]] = []

        # Look for keyword contradictions
        contradiction_pairs = [
            ("mobile", "desktop"),
            ("b2b", "b2c"),
            ("enterprise", "consumer"),
            ("free", "paid"),
            ("freemium", "paid-only"),
            ("self-service", "sales-led"),
            ("low-price", "premium"),
            ("fast", "thorough"),
            ("simple", "feature-rich"),
        ]

        for i, const1 in enumerate(constitutions):
            for const2 in constitutions[i + 1 :]:
                # Only check strategic constitutions against each other
                if (
                    const1.constitution_type.value != "strategic"
                    or const2.constitution_type.value != "strategic"
                ):
                    continue

                # Check each principle pair
                for p1 in const1.principles:
                    for p2 in const2.principles:
                        # Look for contradictions
                        p1_text = (p1.rule + " " + p1.title).lower()
                        p2_text = (p2.rule + " " + p2.title).lower()

                        for word1, word2 in contradiction_pairs:
                            if word1 in p1_text and word2 in p2_text:
                                conflict_desc = (
                                    f"{const1.name}#{p1.principle_id} mentions '{word1}' "
                                    f"but {const2.name}#{p2.principle_id} mentions '{word2}'"
                                )
                                conflicts.append((const1.name, p1.principle_id, conflict_desc))
                            elif word2 in p1_text and word1 in p2_text:
                                conflict_desc = (
                                    f"{const1.name}#{p1.principle_id} mentions '{word2}' "
                                    f"but {const2.name}#{p2.principle_id} mentions '{word1}'"
                                )
                                conflicts.append((const1.name, p1.principle_id, conflict_desc))

        return conflicts

    def check_coverage(
        self, pitch_deck: PitchDeck, constitutions: list[Constitution]
    ) -> list[str]:
        """Check for pitch deck sections not referenced by any constitution.

        Args:
            pitch_deck: PitchDeck object
            constitutions: List of Constitution objects

        Returns:
            List of section IDs with no constitution references

        Example:
            >>> detector = ConflictDetector()
            >>> deck = PitchDeck.parse(Path(".specify/deck/pitch-deck.md"))
            >>> consts = [Constitution.parse(p) for p in Path(".specify/memory/").glob("*.md")]
            >>> gaps = detector.check_coverage(deck, consts)
            >>> gaps
            ['go-to-market', 'financials']
        """
        coverage_gaps: list[str] = []

        # Get all section IDs from pitch deck
        deck_sections = {section.section_id for section in pitch_deck.sections}

        # Get all referenced sections from constitutions
        referenced_sections: set[str] = set()

        for constitution in constitutions:
            for link in constitution.upstream_links:
                # Extract section ID from link
                if link.url and "#" in link.url:
                    section_id = link.url.split("#")[1]
                    referenced_sections.add(section_id)

        # Find sections with no references
        for section_id in deck_sections:
            if section_id not in referenced_sections:
                coverage_gaps.append(section_id)

        return coverage_gaps

    def validate_version_consistency(
        self, pitch_deck: PitchDeck, constitutions: list[Constitution]
    ) -> list[tuple[str, str, str]]:
        """Validate that all constitutions reference the current pitch deck version.

        Args:
            pitch_deck: PitchDeck object with current version
            constitutions: List of Constitution objects

        Returns:
            List of (constitution_name, referenced_version, current_version) tuples
            for constitutions with version mismatches

        Example:
            >>> detector = ConflictDetector()
            >>> deck = PitchDeck.parse(Path(".specify/deck/pitch-deck.md"))
            >>> consts = [Constitution.parse(p) for p in Path(".specify/memory/").glob("*.md")]
            >>> mismatches = detector.validate_version_consistency(deck, consts)
            >>> for name, ref_ver, cur_ver in mismatches:
            ...     print(f"{name} references v{ref_ver} but current is v{cur_ver}")
        """
        version_mismatches: list[tuple[str, str, str]] = []

        current_version = pitch_deck.version

        for constitution in constitutions:
            # For now, we check if constitution version matches deck version
            # In a more sophisticated system, constitutions would explicitly
            # reference the deck version they were derived from
            if constitution.version != current_version:
                version_mismatches.append(
                    (constitution.name, constitution.version, current_version)
                )

        return version_mismatches

    def detect_circular_dependencies(
        self, constitutions: list[Constitution]
    ) -> list[list[str]]:
        """Detect circular dependencies between feature constitutions.

        Args:
            constitutions: List of Constitution objects

        Returns:
            List of cycles, where each cycle is a list of constitution names

        Example:
            >>> detector = ConflictDetector()
            >>> consts = [Constitution.parse(p) for p in Path(".specify/features/").glob("*.md")]
            >>> cycles = detector.detect_circular_dependencies(consts)
            >>> for cycle in cycles:
            ...     print(" -> ".join(cycle))
            001-user-management -> 002-authentication -> 001-user-management
        """
        # Build dependency graph
        graph: dict[str, set[str]] = {}

        for constitution in constitutions:
            deps: set[str] = set()

            # Extract dependencies from upstream links
            for link in constitution.upstream_links:
                if "/features/" in str(link.target_file):
                    target_name = link.target_file.stem
                    deps.add(target_name)

            graph[constitution.name] = deps

        # Find cycles using DFS
        cycles: list[list[str]] = []
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path[:])
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles

    def get_orphaned_principles(
        self, constitutions: list[Constitution]
    ) -> list[tuple[str, str]]:
        """Find principles with no downstream references.

        Args:
            constitutions: List of Constitution objects

        Returns:
            List of (constitution_name, principle_id) tuples for orphaned principles

        Example:
            >>> detector = ConflictDetector()
            >>> consts = [Constitution.parse(p) for p in Path(".specify/memory/").glob("*.md")]
            >>> orphaned = detector.get_orphaned_principles(consts)
            >>> for const_name, principle_id in orphaned:
            ...     print(f"{const_name}#{principle_id} has no downstream references")
        """
        orphaned: list[tuple[str, str]] = []

        # Build set of all referenced principles
        referenced_principles: set[str] = set()

        for constitution in constitutions:
            for link in constitution.upstream_links:
                if link.target_section:
                    # Format: constitution_name#principle_id
                    target_name = link.target_file.stem
                    ref_key = f"{target_name}#{link.target_section}"
                    referenced_principles.add(ref_key)

        # Check which principles are never referenced
        for constitution in constitutions:
            # Only check strategic constitutions (they should be referenced by features)
            if constitution.constitution_type.value == "strategic":
                for principle in constitution.principles:
                    ref_key = f"{constitution.name}#{principle.principle_id}"
                    if ref_key not in referenced_principles:
                        orphaned.append((constitution.name, principle.principle_id))

        return orphaned
