"""Principle extraction with template-guided heuristics."""

import re
from dataclasses import dataclass
from typing import Literal

from ..models.principle import Principle
from ..models.sequoia_section import SequoiaSectionType


@dataclass
class ExtractionPattern:
    """Pattern for extracting principles from text."""

    name: str
    """Pattern name (e.g., 'VALUE_PROP_PATTERN')"""

    regex: str
    """Regular expression pattern"""

    description: str
    """What this pattern detects"""

    confidence: float = 0.8
    """Base confidence for matches (0.0-1.0)"""


class PrincipleExtractor:
    """Extracts principles from pitch deck using heuristic patterns."""

    # Pattern set 1: Value proposition emphasis (ALL_CAPS words)
    VALUE_PROP_PATTERN = ExtractionPattern(
        name="VALUE_PROP",
        regex=r"\b([A-Z][A-Z\s]{2,}[A-Z])\b",
        description="ALL_CAPS emphasis indicating value proposition",
        confidence=0.85,
    )

    # Pattern set 2: Numeric constraints (percentages, commission rates, etc.)
    NUMERIC_CONSTRAINT_PATTERN = ExtractionPattern(
        name="NUMERIC_CONSTRAINT",
        regex=r"(\d+(?:\.\d+)?%?\s*(?:commission|fee|rate|percent|margin|of|users|customers|revenue))",
        description="Numeric business constraints or metrics",
        confidence=0.90,
    )

    # Pattern set 3: Comparative advantages
    COMPARATIVE_PATTERN = ExtractionPattern(
        name="COMPARATIVE",
        regex=r"\b(better|cheaper|faster|easier|more|less|superior|compared to|than|vs\.?)\s+\w+",
        description="Comparative statements indicating competitive advantage",
        confidence=0.75,
    )

    # Pattern set 4: Imperative requirements
    IMPERATIVE_PATTERN = ExtractionPattern(
        name="IMPERATIVE",
        regex=r"\b(must|ensure|require|should|need to|will|guarantee|maintain)\s+\w+",
        description="Imperative statements indicating requirements",
        confidence=0.80,
    )

    # Pattern set 5: Market numbers (TAM, SAM, user counts)
    MARKET_NUMBER_PATTERN = ExtractionPattern(
        name="MARKET_NUMBER",
        regex=r"([\d,]+(?:\.\d+)?(?:\s*(?:million|billion|thousand|M|B|K))?\s*(?:users|customers|people|businesses|market|revenue|\$))",
        description="Market size numbers and user metrics",
        confidence=0.85,
    )

    def __init__(self) -> None:
        """Initialize principle extractor with pattern sets."""
        self.patterns = [
            self.VALUE_PROP_PATTERN,
            self.NUMERIC_CONSTRAINT_PATTERN,
            self.COMPARATIVE_PATTERN,
            self.IMPERATIVE_PATTERN,
            self.MARKET_NUMBER_PATTERN,
        ]

    def extract_principles(
        self,
        text: str,
        section_id: str,
        principle_type: Literal["strategic", "tactical"] = "strategic",
    ) -> list[Principle]:
        """Extract principles from text using heuristic patterns.

        Args:
            text: Source text to analyze
            section_id: Section identifier for source tracking
            principle_type: Type of principles to extract

        Returns:
            List of extracted Principle objects

        Example:
            >>> extractor = PrincipleExtractor()
            >>> text = "10% commission on each transaction. SAVE MONEY when traveling."
            >>> principles = extractor.extract_principles(text, "solution")
            >>> len(principles) >= 2
            True
        """
        principles = []
        principle_id_counter = 1

        # Extract sentences for context
        sentences = self._split_into_sentences(text)

        for sentence in sentences:
            # Try each pattern
            for pattern in self.patterns:
                matches = re.finditer(pattern.regex, sentence, re.IGNORECASE)

                for match in matches:
                    # Extract matched text
                    matched_text = match.group(1) if match.groups() else match.group(0)

                    # Create principle from sentence context
                    principle_text = self._create_principle_statement(
                        matched_text, sentence, pattern
                    )

                    if principle_text:
                        principle = Principle(
                            id=f"principle-{principle_id_counter:03d}",
                            text=principle_text,
                            type=principle_type,
                            source_section_id=section_id,
                            confidence=pattern.confidence,
                            extraction_method="heuristic",
                        )
                        principles.append(principle)
                        principle_id_counter += 1

        # Deduplicate principles with similar text
        principles = self._deduplicate_principles(principles)

        return principles

    def extract_from_bullet_points(
        self, text: str, section_id: str
    ) -> list[Principle]:
        """Extract principles from bulleted list content.

        Args:
            text: Source text containing bullet points
            section_id: Section identifier

        Returns:
            List of Principle objects

        Example:
            >>> extractor = PrincipleExtractor()
            >>> text = "- User registration\\n- Listing management\\n- Booking system"
            >>> principles = extractor.extract_from_bullet_points(text, "product")
            >>> len(principles)
            3
        """
        principles = []
        principle_id_counter = 1

        # Match bullet points (-, *, •, or 1., 2., etc.)
        bullet_pattern = r"^[\s]*[-*•][\s]+(.+)$|^[\s]*\d+\.[\s]+(.+)$"
        lines = text.split("\n")

        for line in lines:
            match = re.match(bullet_pattern, line)
            if match:
                # Get the bullet content (either group 1 or 2 depending on match)
                content = match.group(1) if match.group(1) else match.group(2)
                content = content.strip()

                if len(content) > 5:  # Minimum length filter
                    principle = Principle(
                        id=f"principle-{principle_id_counter:03d}",
                        text=content,
                        type="strategic",
                        source_section_id=section_id,
                        confidence=0.75,  # Lower confidence for bullet extraction
                        extraction_method="heuristic",
                    )
                    principles.append(principle)
                    principle_id_counter += 1

        return principles

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences for analysis.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple sentence splitting (handles . ! ?)
        sentence_pattern = r"[.!?]+\s+"
        sentences = re.split(sentence_pattern, text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]

    def _create_principle_statement(
        self, matched_text: str, sentence: str, pattern: ExtractionPattern
    ) -> str | None:
        """Create principle statement from matched pattern.

        Args:
            matched_text: Text that matched the pattern
            sentence: Full sentence containing the match
            pattern: Pattern that matched

        Returns:
            Principle statement or None if invalid
        """
        # For VALUE_PROP and MARKET_NUMBER patterns, use the matched text directly
        if pattern.name in ["VALUE_PROP", "MARKET_NUMBER"]:
            return matched_text.strip()

        # For other patterns, use the full sentence as context
        # Truncate if too long
        if len(sentence) > 200:
            return None

        return sentence.strip()

    def _deduplicate_principles(self, principles: list[Principle]) -> list[Principle]:
        """Remove duplicate or very similar principles.

        Args:
            principles: List of principles to deduplicate

        Returns:
            Deduplicated list
        """
        if not principles:
            return []

        # Track seen principles by normalized text
        seen = set()
        deduplicated = []

        for principle in principles:
            # Normalize text for comparison
            normalized = principle.text.lower().strip()

            # Remove common punctuation
            normalized = re.sub(r"[.,;:!?]", "", normalized)

            if normalized not in seen:
                seen.add(normalized)
                deduplicated.append(principle)

        return deduplicated

    def enrich_principle_with_rationale(
        self, principle: Principle, section_type: SequoiaSectionType
    ) -> Principle:
        """Add rationale to principle based on section type.

        Args:
            principle: Principle to enrich
            section_type: Sequoia section type

        Returns:
            Enriched principle

        Example:
            >>> extractor = PrincipleExtractor()
            >>> p = Principle(
            ...     id="principle-001",
            ...     text="10% commission",
            ...     type="strategic",
            ...     source_section_id="business-model"
            ... )
            >>> enriched = extractor.enrich_principle_with_rationale(
            ...     p, SequoiaSectionType.BUSINESS_MODEL
            ... )
            >>> enriched.rationale is not None
            True
        """
        # Generate rationale based on section context
        rationale_templates = {
            SequoiaSectionType.COMPANY_PURPOSE: "Defines core mission and organizational identity",
            SequoiaSectionType.PROBLEM: "Addresses fundamental customer pain point",
            SequoiaSectionType.SOLUTION: "Core value proposition differentiator",
            SequoiaSectionType.WHY_NOW: "Market timing and strategic opportunity",
            SequoiaSectionType.MARKET_SIZE: "Market opportunity validation",
            SequoiaSectionType.COMPETITION: "Competitive positioning requirement",
            SequoiaSectionType.PRODUCT: "Product feature requirement",
            SequoiaSectionType.BUSINESS_MODEL: "Business model constraint",
            SequoiaSectionType.TEAM: "Team capability requirement",
            SequoiaSectionType.FINANCIALS: "Financial target or constraint",
        }

        principle.rationale = rationale_templates.get(
            section_type, "Strategic business requirement"
        )

        return principle
