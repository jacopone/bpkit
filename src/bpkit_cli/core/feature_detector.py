"""Feature detection from pitch deck Product and Solution sections."""

import re
from dataclasses import dataclass
from typing import Literal


@dataclass
class DetectedFeature:
    """Represents a detected feature from pitch deck."""

    id: str
    """Feature ID (e.g., '001')"""

    name: str
    """Feature name in kebab-case"""

    title: str
    """Human-readable feature title"""

    description: str
    """Feature description"""

    priority: Literal["P1", "P2", "P3"]
    """Priority level"""

    source_section_id: str
    """Section where feature was detected"""

    confidence: float
    """Detection confidence (0.0-1.0)"""

    keywords: list[str]
    """Keywords that triggered detection"""


class FeatureDetector:
    """Detects MVP features from pitch deck content."""

    # Action verbs indicating features
    FEATURE_ACTION_VERBS = [
        "create",
        "manage",
        "book",
        "search",
        "browse",
        "upload",
        "download",
        "send",
        "receive",
        "process",
        "track",
        "view",
        "edit",
        "delete",
        "share",
        "export",
        "import",
        "connect",
        "integrate",
        "analyze",
        "report",
        "notify",
        "approve",
        "reject",
        "review",
        "rate",
    ]

    # Feature keywords (common nouns for features)
    FEATURE_KEYWORDS = [
        "user",
        "account",
        "profile",
        "listing",
        "product",
        "booking",
        "reservation",
        "payment",
        "transaction",
        "search",
        "filter",
        "dashboard",
        "analytics",
        "report",
        "notification",
        "message",
        "review",
        "rating",
        "comment",
        "feed",
        "timeline",
        "calendar",
        "schedule",
        "settings",
        "preferences",
        "authentication",
        "authorization",
        "registration",
    ]

    def __init__(self) -> None:
        """Initialize feature detector."""
        pass

    def detect_features(self, product_text: str, solution_text: str) -> list[DetectedFeature]:
        """Detect features from Product and Solution sections.

        Args:
            product_text: Text from Product section
            solution_text: Text from Solution section

        Returns:
            List of detected features (5-10 expected)

        Example:
            >>> detector = FeatureDetector()
            >>> product = "User registration, listing management, booking system"
            >>> solution = "SAVE MONEY when traveling. MAKE MONEY when hosting."
            >>> features = detector.detect_features(product, solution)
            >>> len(features) >= 2
            True
        """
        features = []

        # Extract from bullet points first (highest confidence)
        bullet_features = self._extract_from_bullets(product_text, "product")
        features.extend(bullet_features)

        bullet_features_solution = self._extract_from_bullets(solution_text, "solution")
        features.extend(bullet_features_solution)

        # Extract from action verb patterns
        action_features = self._extract_from_action_verbs(product_text, "product")
        features.extend(action_features)

        # Extract from feature keywords
        keyword_features = self._extract_from_keywords(solution_text, "solution")
        features.extend(keyword_features)

        # Deduplicate and prioritize
        features = self._deduplicate_features(features)
        features = self._assign_priorities(features)

        # Limit to 10 features (expected range: 5-10)
        if len(features) > 10:
            # Keep highest confidence features
            features = sorted(features, key=lambda f: f.confidence, reverse=True)[:10]

        # Assign IDs
        for idx, feature in enumerate(features, start=1):
            feature.id = f"{idx:03d}"

        return features

    def _extract_from_bullets(
        self, text: str, section_id: str
    ) -> list[DetectedFeature]:
        """Extract features from bulleted lists.

        Args:
            text: Source text
            section_id: Section identifier

        Returns:
            List of detected features
        """
        features = []

        # Match bullet points
        bullet_pattern = r"^[\s]*[-*•][\s]+(.+)$|^[\s]*\d+\.[\s]+(.+)$"
        lines = text.split("\n")

        for line in lines:
            match = re.match(bullet_pattern, line, re.MULTILINE)
            if match:
                content = match.group(1) if match.group(1) else match.group(2)
                content = content.strip()

                if len(content) > 5:
                    # Extract feature name and description
                    feature_name = self._extract_feature_name(content)
                    if feature_name:
                        feature = DetectedFeature(
                            id="",  # Will be assigned later
                            name=self._to_kebab_case(feature_name),
                            title=feature_name,
                            description=content,
                            priority="P1",  # Will be reassigned
                            source_section_id=section_id,
                            confidence=0.85,  # High confidence for bullets
                            keywords=[feature_name.lower()],
                        )
                        features.append(feature)

        return features

    def _extract_from_action_verbs(
        self, text: str, section_id: str
    ) -> list[DetectedFeature]:
        """Extract features from action verb patterns.

        Args:
            text: Source text
            section_id: Section identifier

        Returns:
            List of detected features
        """
        features = []

        for verb in self.FEATURE_ACTION_VERBS:
            # Pattern: "verb + object" (e.g., "create listings", "manage bookings")
            pattern = rf"\b{verb}\s+(\w+(?:\s+\w+)?)"
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                object_text = match.group(1)
                feature_name = f"{verb.capitalize()} {object_text.capitalize()}"

                feature = DetectedFeature(
                    id="",
                    name=self._to_kebab_case(feature_name),
                    title=feature_name,
                    description=f"Feature: {feature_name}",
                    priority="P2",
                    source_section_id=section_id,
                    confidence=0.70,  # Medium confidence for action verbs
                    keywords=[verb, object_text.lower()],
                )
                features.append(feature)

        return features

    def _extract_from_keywords(
        self, text: str, section_id: str
    ) -> list[DetectedFeature]:
        """Extract features from feature keywords.

        Args:
            text: Source text
            section_id: Section identifier

        Returns:
            List of detected features
        """
        features = []

        for keyword in self.FEATURE_KEYWORDS:
            # Pattern: keyword appears in text
            pattern = rf"\b{keyword}(?:s)?\b"
            if re.search(pattern, text, re.IGNORECASE):
                feature_name = f"{keyword.capitalize()} Management"

                feature = DetectedFeature(
                    id="",
                    name=self._to_kebab_case(feature_name),
                    title=feature_name,
                    description=f"Feature: {feature_name}",
                    priority="P3",
                    source_section_id=section_id,
                    confidence=0.60,  # Lower confidence for keywords alone
                    keywords=[keyword],
                )
                features.append(feature)

        return features

    def _extract_feature_name(self, text: str) -> str | None:
        """Extract clean feature name from text.

        Args:
            text: Source text

        Returns:
            Feature name or None
        """
        # Remove common prefixes
        text = re.sub(r"^(feature:|capability:|component:)\s*", "", text, flags=re.IGNORECASE)

        # Take first few words (max 4)
        words = text.split()[:4]
        feature_name = " ".join(words)

        # Clean up
        feature_name = re.sub(r"[^\w\s-]", "", feature_name)
        feature_name = feature_name.strip()

        return feature_name if len(feature_name) > 3 else None

    def _to_kebab_case(self, text: str) -> str:
        """Convert text to kebab-case.

        Args:
            text: Input text

        Returns:
            Kebab-case string

        Example:
            >>> detector = FeatureDetector()
            >>> detector._to_kebab_case("User Management")
            'user-management'
        """
        # Remove non-alphanumeric except spaces and hyphens
        text = re.sub(r"[^\w\s-]", "", text)
        # Replace spaces with hyphens
        text = re.sub(r"\s+", "-", text)
        # Lowercase
        text = text.lower()
        # Remove consecutive hyphens
        text = re.sub(r"-+", "-", text)
        # Strip leading/trailing hyphens
        text = text.strip("-")
        return text

    def _deduplicate_features(self, features: list[DetectedFeature]) -> list[DetectedFeature]:
        """Remove duplicate features based on name similarity.

        Args:
            features: List of features

        Returns:
            Deduplicated list
        """
        if not features:
            return []

        seen_names = set()
        deduplicated = []

        for feature in features:
            normalized_name = feature.name.lower()
            if normalized_name not in seen_names:
                seen_names.add(normalized_name)
                deduplicated.append(feature)

        return deduplicated

    def _assign_priorities(self, features: list[DetectedFeature]) -> list[DetectedFeature]:
        """Assign priorities based on confidence and position.

        Args:
            features: List of features

        Returns:
            Features with updated priorities
        """
        # Sort by confidence (descending)
        sorted_features = sorted(features, key=lambda f: f.confidence, reverse=True)

        # Assign priorities based on confidence and rank
        for idx, feature in enumerate(sorted_features):
            if idx < 3:
                # Top 3 features are P1
                feature.priority = "P1"
            elif idx < 7:
                # Next 4 features are P2
                feature.priority = "P2"
            else:
                # Remaining features are P3
                feature.priority = "P3"

        return sorted_features
