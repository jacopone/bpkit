"""Entity extraction from pitch deck using hybrid approach.

Extracts entity names and basic relationships, delegates attributes/constraints to Speckit.
"""

import re
from dataclasses import dataclass
from typing import Literal


@dataclass
class EntityRelationship:
    """Relationship between entities."""

    type: Literal["has_many", "belongs_to", "has_one", "many_to_many"]
    """Relationship type"""

    target: str
    """Target entity name"""

    description: str | None = None
    """Optional relationship description"""


@dataclass
class ExtractedEntity:
    """Represents an entity extracted from pitch deck."""

    name: str
    """Entity name in CamelCase"""

    source_link: str
    """Link to pitch deck section"""

    rationale: str
    """Why this entity is needed"""

    relationships: list[EntityRelationship]
    """Relationships to other entities"""

    attribute_suggestions: str | None = None
    """Suggested attributes (TODO placeholder)"""

    constraint_suggestions: str | None = None
    """Suggested constraints (TODO placeholder)"""

    state_suggestions: str | None = None
    """Suggested lifecycle states (TODO placeholder)"""

    confidence: float = 0.80
    """Extraction confidence (0.0-1.0)"""


class EntityExtractor:
    """Extracts entities using hybrid approach (names + relationships, delegate details)."""

    # Common entity patterns (nouns indicating domain objects)
    ENTITY_PATTERNS = [
        "user",
        "customer",
        "account",
        "profile",
        "listing",
        "property",
        "product",
        "item",
        "booking",
        "reservation",
        "order",
        "payment",
        "transaction",
        "invoice",
        "receipt",
        "review",
        "rating",
        "comment",
        "message",
        "notification",
        "event",
        "appointment",
        "schedule",
        "calendar",
        "report",
        "document",
        "file",
        "photo",
        "image",
        "video",
        "category",
        "tag",
        "label",
        "location",
        "address",
        "organization",
        "company",
        "team",
        "member",
    ]

    # Role-based entities (Guest, Host, Admin, etc.)
    ROLE_PATTERNS = [
        "guest",
        "host",
        "admin",
        "owner",
        "manager",
        "staff",
        "customer",
        "client",
        "vendor",
        "supplier",
        "partner",
    ]

    def __init__(self) -> None:
        """Initialize entity extractor."""
        pass

    def extract_entities(
        self, product_text: str, solution_text: str, business_model_text: str
    ) -> list[ExtractedEntity]:
        """Extract entities from key pitch deck sections.

        Args:
            product_text: Text from Product section
            solution_text: Text from Solution section
            business_model_text: Text from Business Model section

        Returns:
            List of extracted entities with relationships

        Example:
            >>> extractor = EntityExtractor()
            >>> product = "Users can create listings and receive bookings."
            >>> solution = "Connect guests with hosts."
            >>> business = "10% commission on transactions."
            >>> entities = extractor.extract_entities(product, solution, business)
            >>> len(entities) >= 3  # User, Listing, Booking
            True
        """
        entities = []

        # Combine all text for entity detection
        combined_text = f"{product_text}\n{solution_text}\n{business_model_text}"

        # Extract entities using patterns
        detected_entity_names = self._detect_entity_names(combined_text)

        # Create entity objects with inferred relationships
        for entity_name in detected_entity_names:
            entity = self._create_entity(
                entity_name, combined_text, detected_entity_names
            )
            if entity:
                entities.append(entity)

        # Deduplicate by name
        entities = self._deduplicate_entities(entities)

        return entities

    def _detect_entity_names(self, text: str) -> set[str]:
        """Detect entity names from text.

        Args:
            text: Source text

        Returns:
            Set of detected entity names (capitalized)
        """
        detected = set()

        # Check for explicit entity patterns
        for pattern in self.ENTITY_PATTERNS:
            # Look for singular or plural forms
            regex = rf"\b{pattern}(?:s)?\b"
            if re.search(regex, text, re.IGNORECASE):
                # Capitalize entity name
                entity_name = pattern.capitalize()
                detected.add(entity_name)

        # Check for role-based entities
        for role in self.ROLE_PATTERNS:
            regex = rf"\b{role}(?:s)?\b"
            if re.search(regex, text, re.IGNORECASE):
                entity_name = role.capitalize()
                detected.add(entity_name)

        return detected

    def _create_entity(
        self, entity_name: str, full_text: str, all_entities: set[str]
    ) -> ExtractedEntity | None:
        """Create entity object with inferred relationships.

        Args:
            entity_name: Name of entity (capitalized)
            full_text: Full text for context
            all_entities: Set of all detected entity names

        Returns:
            ExtractedEntity or None if invalid
        """
        # Infer relationships based on common patterns
        relationships = self._infer_relationships(entity_name, full_text, all_entities)

        # Generate rationale based on entity type
        rationale = self._generate_rationale(entity_name)

        # Suggest attributes, constraints, and states
        attribute_suggestions = self._suggest_attributes(entity_name)
        constraint_suggestions = self._suggest_constraints(entity_name)
        state_suggestions = self._suggest_states(entity_name)

        entity = ExtractedEntity(
            name=entity_name,
            source_link="pitch-deck.md#product",  # Default, will be refined later
            rationale=rationale,
            relationships=relationships,
            attribute_suggestions=attribute_suggestions,
            constraint_suggestions=constraint_suggestions,
            state_suggestions=state_suggestions,
            confidence=0.80,
        )

        return entity

    def _infer_relationships(
        self, entity_name: str, text: str, all_entities: set[str]
    ) -> list[EntityRelationship]:
        """Infer relationships between entities based on text patterns.

        Args:
            entity_name: Current entity name
            text: Full text for analysis
            all_entities: All detected entities

        Returns:
            List of inferred relationships
        """
        relationships = []

        # Common relationship patterns
        # Pattern 1: "users have bookings" → User has_many Booking
        has_many_pattern = rf"{entity_name.lower()}(?:s)?\s+(?:have|has|own|create|manage)\s+(\w+)"
        matches = re.finditer(has_many_pattern, text, re.IGNORECASE)
        for match in matches:
            target = match.group(1).capitalize()
            if target in all_entities:
                relationships.append(
                    EntityRelationship(
                        type="has_many",
                        target=target,
                        description=f"inferred from 'have/own' pattern",
                    )
                )

        # Pattern 2: "bookings belong to users" → Booking belongs_to User
        belongs_to_pattern = rf"{entity_name.lower()}(?:s)?\s+(?:belong to|is owned by|created by)\s+(\w+)"
        matches = re.finditer(belongs_to_pattern, text, re.IGNORECASE)
        for match in matches:
            target = match.group(1).capitalize()
            if target in all_entities:
                relationships.append(
                    EntityRelationship(
                        type="belongs_to",
                        target=target,
                        description=f"inferred from 'belong to' pattern",
                    )
                )

        # Fallback: Add generic relationship to User if detected
        if "User" in all_entities and entity_name != "User" and not relationships:
            relationships.append(
                EntityRelationship(
                    type="belongs_to",
                    target="User",
                    description="generic user association",
                )
            )

        return relationships

    def _generate_rationale(self, entity_name: str) -> str:
        """Generate rationale for why entity is needed.

        Args:
            entity_name: Entity name

        Returns:
            Rationale string
        """
        rationale_templates = {
            "User": "Core user role for platform",
            "Listing": "Central entity representing items/properties",
            "Booking": "Represents transactions/reservations",
            "Payment": "Handles financial transactions",
            "Review": "User-generated feedback",
            "Message": "Communication between users",
            "Notification": "System-generated alerts",
        }

        return rationale_templates.get(entity_name, f"Domain entity for {entity_name.lower()} management")

    def _suggest_attributes(self, entity_name: str) -> str:
        """Suggest attributes for entity (TODO placeholder).

        Args:
            entity_name: Entity name

        Returns:
            Attribute suggestions
        """
        common_attributes = "id, created_at, updated_at"

        suggestions = {
            "User": f"{common_attributes}, email, name, role",
            "Listing": f"{common_attributes}, title, description, price",
            "Booking": f"{common_attributes}, check_in_date, check_out_date, status, total_price",
            "Payment": f"{common_attributes}, amount, currency, status, transaction_id",
            "Review": f"{common_attributes}, rating, comment, verified",
        }

        return suggestions.get(entity_name, common_attributes)

    def _suggest_constraints(self, entity_name: str) -> str:
        """Suggest constraints for entity (TODO placeholder).

        Args:
            entity_name: Entity name

        Returns:
            Constraint suggestions
        """
        constraints = {
            "User": "email format validation, unique email",
            "Listing": "price > 0, title max length 200",
            "Booking": "check_in < check_out, total_price > 0",
            "Payment": "amount > 0, valid currency code",
            "Review": "rating 1-5, comment max length 1000",
        }

        return constraints.get(entity_name, "Define validation rules")

    def _suggest_states(self, entity_name: str) -> str:
        """Suggest lifecycle states for entity (TODO placeholder).

        Args:
            entity_name: Entity name

        Returns:
            State suggestions
        """
        states = {
            "User": "registered, verified, active, suspended",
            "Listing": "draft, published, booked, archived",
            "Booking": "PENDING, CONFIRMED, ACTIVE, COMPLETED, CANCELLED",
            "Payment": "pending, processing, completed, failed, refunded",
            "Review": "pending, published, flagged, removed",
        }

        return states.get(entity_name, "Define entity states")

    def _deduplicate_entities(self, entities: list[ExtractedEntity]) -> list[ExtractedEntity]:
        """Remove duplicate entities by name.

        Args:
            entities: List of entities

        Returns:
            Deduplicated list
        """
        seen_names = set()
        deduplicated = []

        for entity in entities:
            if entity.name not in seen_names:
                seen_names.add(entity.name)
                deduplicated.append(entity)

        return deduplicated
