"""Clarification question models for BP-Kit quality commands."""

from enum import Enum
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from .pitch_deck import PitchDeck


class Priority(str, Enum):
    """Priority level for clarification questions."""

    HIGH = "high"  # Scope-impacting, financial, security
    MEDIUM = "medium"  # Strategy, user experience
    LOW = "low"  # Details, polish, nice-to-have


class ClarificationQuestion:
    """Represents an ambiguity requiring user input."""

    def __init__(
        self,
        question_id: str,
        question_text: str,
        section_id: str,
        priority: Priority,
        suggested_answers: list[str] | None = None,
        user_answer: str | None = None,
    ) -> None:
        """Initialize clarification question.

        Args:
            question_id: Unique ID (e.g., 'CLQ001', 'CLQ002')
            question_text: The question to ask
            section_id: Which pitch deck section this relates to
            priority: HIGH, MEDIUM, or LOW
            suggested_answers: Pre-populated answer options
            user_answer: User's response (populated after ask_interactively)
        """
        self.question_id = question_id
        self.question_text = question_text
        self.section_id = section_id
        self.priority = priority
        self.suggested_answers = suggested_answers or []
        self.user_answer = user_answer

    def ask_interactively(self, console: Console | None = None) -> str:
        """Prompt user for answer interactively.

        Args:
            console: Rich console instance (creates new if None)

        Returns:
            User's answer string

        Example:
            >>> question = ClarificationQuestion(
            ...     "CLQ001",
            ...     "Who are your top 3 competitors?",
            ...     "competition",
            ...     Priority.HIGH,
            ...     ["Airbnb, Vrbo, Booking.com", "Traditional hotels", "Custom answer"]
            ... )
            >>> answer = question.ask_interactively()  # Prompts user
        """
        if console is None:
            console = Console()

        # Display question header
        console.print(f"\n[bold cyan]Question {self.question_id}[/bold cyan]")
        console.print(f"[bold]Section:[/bold] {self.section_id}")
        console.print(f"[bold]Priority:[/bold] {self.priority.value.upper()}")
        console.print(f"\n[bold yellow]{self.question_text}[/bold yellow]\n")

        # Display suggested answers if available
        if self.suggested_answers:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Option", style="cyan", width=8)
            table.add_column("Answer", style="white")

            for i, answer in enumerate(self.suggested_answers):
                option_letter = chr(65 + i)  # A, B, C, ...
                table.add_row(option_letter, answer)

            console.print(table)
            console.print()

            # Prompt for selection
            valid_options = [chr(65 + i) for i in range(len(self.suggested_answers))]
            prompt_text = (
                f"Select option ({', '.join(valid_options)}) or enter custom answer"
            )

            answer = Prompt.ask(prompt_text)

            # Check if user selected a letter option
            answer_upper = answer.upper()
            if answer_upper in valid_options:
                idx = ord(answer_upper) - 65
                self.user_answer = self.suggested_answers[idx]
            else:
                # Custom answer
                self.user_answer = answer
        else:
            # No suggested answers, free-form input
            self.user_answer = Prompt.ask("Your answer")

        return self.user_answer

    def update_pitch_deck(self, deck: PitchDeck) -> None:
        """Update pitch deck section with this answer.

        Args:
            deck: PitchDeck instance to update

        Raises:
            ValueError: If section not found or no answer provided
        """
        if not self.user_answer:
            raise ValueError(f"Question {self.question_id} has no answer to apply")

        section = deck.get_section(self.section_id)
        if section is None:
            raise ValueError(
                f"Section '{self.section_id}' not found in pitch deck for question {self.question_id}"
            )

        # Append answer to section content
        # Note: This is a simple implementation. More sophisticated merging
        # could preserve structure, replace placeholders, etc.
        if section.content.strip():
            updated_content = f"{section.content.rstrip()}\n\n{self.user_answer}"
        else:
            updated_content = self.user_answer

        deck.update_section(self.section_id, updated_content)

    def __repr__(self) -> str:
        answered = "answered" if self.user_answer else "pending"
        return (
            f"ClarificationQuestion(id='{self.question_id}', section='{self.section_id}', "
            f"priority={self.priority.value}, status={answered})"
        )
