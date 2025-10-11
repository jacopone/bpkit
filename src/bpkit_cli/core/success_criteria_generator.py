"""Success criteria generation using two-tier hybrid approach.

Tier 1 (60-80%): Derive concrete criteria from clear business metrics
Tier 2 (20-40%): Generate structured placeholders with guidance for ambiguous metrics
"""

import re
from dataclasses import dataclass
from typing import Literal


@dataclass
class SuccessCriterion:
    """Represents a success criterion for a feature."""

    id: str
    """Criterion ID (e.g., 'SC-004-001')"""

    text: str
    """Criterion statement"""

    type: Literal["derived", "placeholder"]
    """Whether derived from pitch deck or placeholder"""

    source_link: str
    """Link to pitch deck section"""

    # Fields for derived criteria
    rationale: str | None = None
    """Why this criterion matters (derived only)"""

    test: str | None = None
    """How to test this criterion (derived only)"""

    confidence: float = 0.95
    """Confidence in derivation (derived only)"""

    # Fields for placeholder criteria
    business_goal: str | None = None
    """Business goal this supports (placeholder only)"""

    suggested_approaches: list[str] | None = None
    """Suggested approaches for user to consider (placeholder only)"""


class SuccessCriteriaGenerator:
    """Generates success criteria using two-tier hybrid approach."""

    def __init__(self) -> None:
        """Initialize success criteria generator."""
        pass

    def generate_criteria(
        self,
        business_model_text: str,
        product_text: str,
        feature_name: str,
        feature_id: str,
    ) -> list[SuccessCriterion]:
        """Generate success criteria for a feature.

        Args:
            business_model_text: Text from Business Model section
            product_text: Text from Product section
            feature_name: Name of the feature
            feature_id: Feature ID (e.g., '004')

        Returns:
            List of success criteria (derived + placeholder)

        Example:
            >>> generator = SuccessCriteriaGenerator()
            >>> business = "10% commission on each transaction. $70/night average."
            >>> product = "Booking system for travelers."
            >>> criteria = generator.generate_criteria(business, product, "Booking System", "004")
            >>> len(criteria) >= 2
            True
        """
        criteria = []
        criterion_counter = 1

        # Tier 1: Derive criteria from business metrics
        # Rule 1: Commission rates → Accuracy requirements
        commission_criteria = self._derive_commission_criteria(
            business_model_text, feature_id, criterion_counter
        )
        if commission_criteria:
            criteria.append(commission_criteria)
            criterion_counter += 1

        # Rule 2: Pricing → Precision requirements
        pricing_criteria = self._derive_pricing_criteria(
            business_model_text, feature_id, criterion_counter
        )
        if pricing_criteria:
            criteria.append(pricing_criteria)
            criterion_counter += 1

        # Rule 3: Scale (user counts) → Performance requirements
        scale_criteria = self._derive_scale_criteria(
            business_model_text, product_text, feature_id, criterion_counter
        )
        if scale_criteria:
            criteria.append(scale_criteria)
            criterion_counter += 1

        # Rule 4: Criticality → Availability requirements
        criticality_criteria = self._derive_criticality_criteria(
            feature_name, feature_id, criterion_counter
        )
        if criticality_criteria:
            criteria.append(criticality_criteria)
            criterion_counter += 1

        # Tier 2: Generate placeholder for conversion/user satisfaction
        placeholder = self._generate_placeholder_criterion(
            feature_name, feature_id, criterion_counter
        )
        criteria.append(placeholder)

        return criteria

    def _derive_commission_criteria(
        self, text: str, feature_id: str, counter: int
    ) -> SuccessCriterion | None:
        """Derive commission accuracy criterion.

        Args:
            text: Business model text
            feature_id: Feature ID
            counter: Criterion counter

        Returns:
            SuccessCriterion or None
        """
        # Pattern: X% commission/fee
        pattern = r"(\d+(?:\.\d+)?)\s*%\s*(?:commission|fee)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            percentage = match.group(1)
            criterion = SuccessCriterion(
                id=f"SC-{feature_id}-{counter:03d}",
                text=f"Commission calculation accurate to 0.01% (verified against manual calculation for {percentage}% rate)",
                type="derived",
                source_link="pitch-deck.md#business-model",
                rationale=f"Business model depends on {percentage}% commission - calculation errors directly impact revenue",
                test=f"Unit tests verify commission = booking_amount * {float(percentage) / 100:.2f} for all transaction types",
                confidence=0.95,
            )
            return criterion

        return None

    def _derive_pricing_criteria(
        self, text: str, feature_id: str, counter: int
    ) -> SuccessCriterion | None:
        """Derive pricing precision criterion.

        Args:
            text: Business model text
            feature_id: Feature ID
            counter: Criterion counter

        Returns:
            SuccessCriterion or None
        """
        # Pattern: $X amount or pricing mention
        pattern = r"\$(\d+(?:,\d+)?(?:\.\d+)?)"
        match = re.search(pattern, text)

        if match:
            amount = match.group(1)
            criterion = SuccessCriterion(
                id=f"SC-{feature_id}-{counter:03d}",
                text="Pricing display accurate to 2 decimal places",
                type="derived",
                source_link="pitch-deck.md#business-model",
                rationale=f"Business model involves ${amount} transactions - pricing must be precise",
                test="Pricing calculations never lose precision beyond 2 decimals",
                confidence=0.95,
            )
            return criterion

        return None

    def _derive_scale_criteria(
        self, business_text: str, product_text: str, feature_id: str, counter: int
    ) -> SuccessCriterion | None:
        """Derive performance criterion from scale metrics.

        Args:
            business_text: Business model text
            product_text: Product text
            feature_id: Feature ID
            counter: Criterion counter

        Returns:
            SuccessCriterion or None
        """
        # Pattern: Large numbers indicating scale
        combined = f"{business_text} {product_text}"
        pattern = r"([\d,]+)\s*(?:users|customers|transactions|bookings)"
        match = re.search(pattern, combined, re.IGNORECASE)

        if match:
            count_str = match.group(1).replace(",", "")
            try:
                count = int(count_str)
                if count >= 10000:  # Only create criterion for significant scale
                    criterion = SuccessCriterion(
                        id=f"SC-{feature_id}-{counter:03d}",
                        text=f"System handles {count_str}+ concurrent users with <2s response time",
                        type="derived",
                        source_link="pitch-deck.md#business-model",
                        rationale=f"Target market size of {count_str} users requires scalable performance",
                        test="Load testing with simulated user traffic validates response times",
                        confidence=0.90,
                    )
                    return criterion
            except ValueError:
                pass

        return None

    def _derive_criticality_criteria(
        self, feature_name: str, feature_id: str, counter: int
    ) -> SuccessCriterion | None:
        """Derive availability criterion for critical features.

        Args:
            feature_name: Name of feature
            feature_id: Feature ID
            counter: Criterion counter

        Returns:
            SuccessCriterion or None
        """
        # Critical features requiring high availability
        critical_keywords = [
            "payment",
            "transaction",
            "booking",
            "authentication",
            "authorization",
            "checkout",
        ]

        feature_lower = feature_name.lower()
        is_critical = any(keyword in feature_lower for keyword in critical_keywords)

        if is_critical:
            criterion = SuccessCriterion(
                id=f"SC-{feature_id}-{counter:03d}",
                text="Feature availability >99.5% (measured monthly)",
                type="derived",
                source_link="pitch-deck.md#product",
                rationale=f"{feature_name} is business-critical - downtime directly impacts revenue",
                test="Uptime monitoring and incident tracking validate availability target",
                confidence=0.90,
            )
            return criterion

        return None

    def _generate_placeholder_criterion(
        self, feature_name: str, feature_id: str, counter: int
    ) -> SuccessCriterion:
        """Generate placeholder criterion with guidance.

        Args:
            feature_name: Name of feature
            feature_id: Feature ID
            counter: Criterion counter

        Returns:
            SuccessCriterion with placeholder type
        """
        # Generate placeholder for user conversion/satisfaction
        business_goal = self._infer_business_goal(feature_name)
        suggested_approaches = self._generate_suggestions(feature_name)

        criterion = SuccessCriterion(
            id=f"SC-{feature_id}-{counter:03d}",
            text=f"[Success criterion supporting {business_goal.lower()}] ⚠️ PLACEHOLDER",
            type="placeholder",
            source_link="pitch-deck.md#business-model",
            business_goal=business_goal,
            suggested_approaches=suggested_approaches,
        )

        return criterion

    def _infer_business_goal(self, feature_name: str) -> str:
        """Infer business goal from feature name.

        Args:
            feature_name: Name of feature

        Returns:
            Business goal description
        """
        goal_mapping = {
            "booking": "Achieve sustainable booking volume",
            "payment": "Maximize payment success rate",
            "search": "Improve search conversion rate",
            "user": "Drive user registration and activation",
            "listing": "Increase listing creation rate",
            "review": "Encourage user engagement and trust",
            "notification": "Maintain user engagement",
        }

        feature_lower = feature_name.lower()
        for keyword, goal in goal_mapping.items():
            if keyword in feature_lower:
                return goal

        return "Support business objectives"

    def _generate_suggestions(self, feature_name: str) -> list[str]:
        """Generate suggested approaches for placeholder criterion.

        Args:
            feature_name: Name of feature

        Returns:
            List of suggested approaches
        """
        # Generic suggestions
        suggestions = [
            "User satisfaction score >80% (post-feature survey)",
            "Feature adoption rate >60% within 30 days",
            "Task completion rate >90%",
        ]

        # Feature-specific suggestions
        feature_lower = feature_name.lower()

        if "booking" in feature_lower:
            suggestions = [
                "Booking completion time <5 minutes",
                "Booking abandonment rate <20%",
                "Payment success rate >95%",
            ]
        elif "search" in feature_lower:
            suggestions = [
                "Search results returned in <1 second",
                "Search-to-click rate >40%",
                "Zero-result searches <10%",
            ]
        elif "payment" in feature_lower:
            suggestions = [
                "Payment processing time <30 seconds",
                "Payment failure rate <5%",
                "Refund processing time <24 hours",
            ]
        elif "user" in feature_lower or "registration" in feature_lower:
            suggestions = [
                "Registration completion rate >80%",
                "Email verification rate >70%",
                "Time to first action <5 minutes after registration",
            ]

        return suggestions
