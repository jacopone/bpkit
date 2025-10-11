"""Ambiguity detection for pitch deck sections."""

import re
from pathlib import Path

from ..models.clarification import ClarificationQuestion, Priority
from ..models.pitch_deck import PitchDeck, PitchDeckSection


class AmbiguityDetector:
    """Detect vague or incomplete sections in pitch decks."""

    # Sequoia template required sections
    REQUIRED_SECTIONS = [
        "company-purpose",
        "problem",
        "solution",
        "why-now",
        "market-potential",
        "competition",
        "business-model",
        "team",
    ]

    # Priority mapping for sections
    SECTION_PRIORITY = {
        "business-model": Priority.HIGH,  # Financial/revenue
        "market-potential": Priority.HIGH,  # Market size
        "problem": Priority.HIGH,  # Core value prop
        "solution": Priority.HIGH,  # Core value prop
        "competition": Priority.MEDIUM,  # Strategy
        "why-now": Priority.MEDIUM,  # Timing/strategy
        "company-purpose": Priority.MEDIUM,  # Vision
        "team": Priority.LOW,  # Details
        "go-to-market": Priority.MEDIUM,  # Strategy
        "financials": Priority.HIGH,  # Numbers
    }

    def __init__(self) -> None:
        """Initialize ambiguity detector."""
        pass

    def detect_vague_sections(
        self, deck: PitchDeck, target_section: str | None = None
    ) -> list[PitchDeckSection]:
        """Detect sections that are vague or incomplete.

        Args:
            deck: PitchDeck instance
            target_section: Optional section ID to focus on (None = all sections)

        Returns:
            List of vague PitchDeckSections, ordered by priority

        Example:
            >>> deck = PitchDeck.parse(Path(".specify/deck/pitch-deck.md"))
            >>> detector = AmbiguityDetector()
            >>> vague = detector.detect_vague_sections(deck)
            >>> len(vague)
            3
        """
        vague_sections: list[tuple[PitchDeckSection, Priority]] = []

        sections_to_check = (
            [deck.get_section(target_section)] if target_section else deck.sections
        )

        for section in sections_to_check:
            if section is None:
                continue

            # Check if section is empty
            if section.is_empty():
                priority = self.SECTION_PRIORITY.get(section.section_id, Priority.MEDIUM)
                vague_sections.append((section, priority))
                continue

            # Check for vague indicators
            vague_indicators = section.detect_vagueness()
            if vague_indicators:
                priority = self.SECTION_PRIORITY.get(section.section_id, Priority.MEDIUM)
                vague_sections.append((section, priority))
                continue

            # Check word count (too short = likely incomplete)
            word_count = section.get_word_count()
            if word_count < 20:  # Arbitrary threshold
                priority = self.SECTION_PRIORITY.get(section.section_id, Priority.LOW)
                vague_sections.append((section, priority))

        # Sort by priority (HIGH > MEDIUM > LOW)
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        vague_sections.sort(key=lambda x: priority_order[x[1]])

        return [section for section, _ in vague_sections]

    def generate_question(self, section: PitchDeckSection, question_id: str) -> ClarificationQuestion:
        """Generate a clarification question for a vague section.

        Args:
            section: PitchDeckSection that needs clarification
            question_id: Unique question ID

        Returns:
            ClarificationQuestion instance

        Example:
            >>> section = PitchDeckSection("competition", "Competition", "[TBD]", 10, 11)
            >>> detector = AmbiguityDetector()
            >>> question = detector.generate_question(section, "CLQ001")
            >>> "competitors" in question.question_text.lower()
            True
        """
        priority = self.SECTION_PRIORITY.get(section.section_id, Priority.MEDIUM)

        # Generate section-specific questions
        if section.section_id == "competition":
            return ClarificationQuestion(
                question_id=question_id,
                question_text="Who are your top 3 direct competitors and what is your specific advantage over each?",
                section_id=section.section_id,
                priority=priority,
                suggested_answers=[
                    "Airbnb, Vrbo, Booking.com - advantage is local authenticity",
                    "Traditional hotel chains - advantage is lower prices",
                    "Custom answer",
                ],
            )

        elif section.section_id == "business-model":
            return ClarificationQuestion(
                question_id=question_id,
                question_text="What are your target unit economics? (CAC, LTV, margins, payback period)",
                section_id=section.section_id,
                priority=priority,
                suggested_answers=[
                    "CAC: $50, LTV: $300, Margin: 15%, Payback: 3 months",
                    "CAC: $100, LTV: $250, Margin: 10%, Payback: 6 months",
                    "Custom answer",
                ],
            )

        elif section.section_id == "market-potential":
            return ClarificationQuestion(
                question_id=question_id,
                question_text="What is your total addressable market (TAM) and serviceable addressable market (SAM)?",
                section_id=section.section_id,
                priority=priority,
                suggested_answers=[
                    "TAM: $10B, SAM: $1B, targeting 5% market share in 5 years",
                    "TAM: $50B, SAM: $5B, targeting 1% market share in 3 years",
                    "Custom answer",
                ],
            )

        elif section.section_id == "problem":
            return ClarificationQuestion(
                question_id=question_id,
                question_text="What is the specific problem you're solving and who experiences it most acutely?",
                section_id=section.section_id,
                priority=priority,
                suggested_answers=[
                    "High transaction costs for peer-to-peer rentals, affecting property owners",
                    "Lack of trust in online marketplaces, affecting buyers",
                    "Custom answer",
                ],
            )

        elif section.section_id == "solution":
            return ClarificationQuestion(
                question_id=question_id,
                question_text="What is your core solution and what makes it 10x better than alternatives?",
                section_id=section.section_id,
                priority=priority,
                suggested_answers=[
                    "Platform with verified reviews and instant booking - 10x faster than traditional",
                    "AI-powered matching that reduces search time by 80%",
                    "Custom answer",
                ],
            )

        elif section.section_id == "why-now":
            return ClarificationQuestion(
                question_id=question_id,
                question_text="Why is now the right time for this solution? What has changed?",
                section_id=section.section_id,
                priority=priority,
                suggested_answers=[
                    "Remote work explosion increased demand for flexible housing by 300%",
                    "New regulations enable our business model",
                    "Custom answer",
                ],
            )

        elif section.section_id == "company-purpose":
            return ClarificationQuestion(
                question_id=question_id,
                question_text="What is your company's core mission in one sentence?",
                section_id=section.section_id,
                priority=priority,
                suggested_answers=[
                    "Make travel more accessible and authentic for everyone",
                    "Democratize access to financial services for underbanked populations",
                    "Custom answer",
                ],
            )

        elif section.section_id == "team":
            return ClarificationQuestion(
                question_id=question_id,
                question_text="What makes your founding team uniquely qualified to solve this problem?",
                section_id=section.section_id,
                priority=priority,
                suggested_answers=[
                    "10+ years combined experience in industry, previous successful exit",
                    "Technical expertise (2x PhDs) + domain expertise (former industry exec)",
                    "Custom answer",
                ],
            )

        elif section.section_id == "go-to-market":
            return ClarificationQuestion(
                question_id=question_id,
                question_text="What is your go-to-market strategy and customer acquisition approach?",
                section_id=section.section_id,
                priority=priority,
                suggested_answers=[
                    "Direct sales to enterprises + viral referral loop",
                    "Content marketing + SEO + paid ads",
                    "Custom answer",
                ],
            )

        else:
            # Generic question for other sections
            return ClarificationQuestion(
                question_id=question_id,
                question_text=f"Please provide details for the '{section.title}' section.",
                section_id=section.section_id,
                priority=priority,
                suggested_answers=["Custom answer"],
            )

    def prioritize_questions(
        self, questions: list[ClarificationQuestion], max_questions: int = 5
    ) -> list[ClarificationQuestion]:
        """Prioritize and limit questions to maximum count.

        Args:
            questions: List of all clarification questions
            max_questions: Maximum number to return (default 5)

        Returns:
            Top priority questions, limited to max_questions

        Example:
            >>> questions = [
            ...     ClarificationQuestion("Q1", "...", "team", Priority.LOW, []),
            ...     ClarificationQuestion("Q2", "...", "problem", Priority.HIGH, []),
            ... ]
            >>> detector = AmbiguityDetector()
            >>> top = detector.prioritize_questions(questions, max_questions=1)
            >>> top[0].priority
            <Priority.HIGH: 'high'>
        """
        # Sort by priority (HIGH > MEDIUM > LOW)
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        sorted_questions = sorted(questions, key=lambda q: priority_order[q.priority])

        return sorted_questions[:max_questions]
