"""Constitutional generator - Orchestrates pitch deck decomposition."""

from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from ..models.decomposition import DecompositionCounts, DecompositionMode, DecompositionResult
from ..models.pitch_deck import PitchDeck
from ..models.principle import Principle
from ..models.sequoia_section import (
    SequoiaSectionType,
    get_constitution_type,
    get_strategic_constitution_types,
)
from .entity_extractor import EntityExtractor, ExtractedEntity
from .feature_detector import DetectedFeature, FeatureDetector
from .principle_extractor import PrincipleExtractor
from .sequoia_parser import SequoiaParser
from .success_criteria_generator import SuccessCriteriaGenerator, SuccessCriterion


class ConstitutionGenerator:
    """Generates constitutional specifications from pitch deck."""

    def __init__(self, project_root: Path) -> None:
        """Initialize constitution generator.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
        self.templates_dir = Path(__file__).parent.parent / "templates"

        # Initialize Jinja2 environment
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_dir)))

        # Initialize extractors
        self.sequoia_parser = SequoiaParser()
        self.principle_extractor = PrincipleExtractor()
        self.feature_detector = FeatureDetector()
        self.entity_extractor = EntityExtractor()
        self.success_criteria_generator = SuccessCriteriaGenerator()

    def generate_all_constitutions(
        self, pitch_deck: PitchDeck, mode: DecompositionMode, dry_run: bool = False
    ) -> DecompositionResult:
        """Generate all constitutions from pitch deck.

        Args:
            pitch_deck: Parsed pitch deck
            mode: Decomposition mode
            dry_run: If True, don't write files

        Returns:
            DecompositionResult with statistics and paths

        Example:
            >>> generator = ConstitutionGenerator(Path.cwd())
            >>> deck = PitchDeck.parse(Path(".specify/deck/pitch-deck.md"))
            >>> result = generator.generate_all_constitutions(deck, DecompositionMode.FROM_FILE)
            >>> result.is_success()
            True
        """
        result = DecompositionResult(
            mode=mode,
            pitch_deck_path=pitch_deck.file_path,
            pitch_deck_version=pitch_deck.version,
            dry_run=dry_run,
        )

        try:
            # Step 1: Generate 4 strategic constitutions
            strategic_constitutions = self._generate_strategic_constitutions(pitch_deck)
            result.counts.strategic_constitutions = len(strategic_constitutions)

            # Step 2: Detect features from Product and Solution sections
            product_text = self.sequoia_parser.extract_section_text(pitch_deck, "product")
            solution_text = self.sequoia_parser.extract_section_text(pitch_deck, "solution")
            detected_features = self.feature_detector.detect_features(product_text, solution_text)

            # Step 3: Generate feature constitutions
            business_model_text = self.sequoia_parser.extract_section_text(
                pitch_deck, "business-model"
            )
            feature_constitutions = self._generate_feature_constitutions(
                detected_features, product_text, solution_text, business_model_text, pitch_deck
            )
            result.counts.feature_constitutions = len(feature_constitutions)

            # Step 4: Count statistics
            result.counts = self._count_statistics(
                strategic_constitutions, feature_constitutions
            )

            # Step 5: Write files (unless dry-run)
            if not dry_run:
                self._write_constitutions(strategic_constitutions, feature_constitutions)

        except Exception as e:
            # Add error to result
            from ..models.decomposition import DecompositionError

            result.errors.append(
                DecompositionError(
                    code="GENERATION_FAILED",
                    message=str(e),
                    recoverable=False,
                )
            )

        return result

    def _generate_strategic_constitutions(self, pitch_deck: PitchDeck) -> dict[str, dict]:
        """Generate 4 strategic constitutions.

        Args:
            pitch_deck: Parsed pitch deck

        Returns:
            Dictionary mapping constitution type to constitution data
        """
        constitutions = {}

        for constitution_type in get_strategic_constitution_types():
            # Get relevant sections for this constitution
            sections = self.sequoia_parser.get_sections_for_constitution(
                pitch_deck, constitution_type
            )

            # Extract principles from all relevant sections
            principles = []
            for section in sections:
                section_type = SequoiaSectionType(section.section_id)
                section_principles = self.principle_extractor.extract_principles(
                    section.content, section.section_id, principle_type="strategic"
                )

                # Enrich principles with rationale
                for principle in section_principles:
                    principle = self.principle_extractor.enrich_principle_with_rationale(
                        principle, section_type
                    )
                    principles.append(principle)

            # Prepare constitution data
            constitution_name = constitution_type.replace("-constitution.md", "").title()
            constitution_data = {
                "constitution_type": constitution_name,
                "version": pitch_deck.version,
                "pitch_deck_version": pitch_deck.version,
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "updated_date": datetime.now().strftime("%Y-%m-%d"),
                "source_sections": [s.section_id for s in sections],
                "principles": principles,
            }

            constitutions[constitution_type] = constitution_data

        return constitutions

    def _generate_feature_constitutions(
        self,
        detected_features: list[DetectedFeature],
        product_text: str,
        solution_text: str,
        business_model_text: str,
        pitch_deck: PitchDeck,
    ) -> dict[str, dict]:
        """Generate feature constitutions.

        Args:
            detected_features: List of detected features
            product_text: Product section text
            solution_text: Solution section text
            business_model_text: Business Model section text
            pitch_deck: Parsed pitch deck

        Returns:
            Dictionary mapping feature filename to feature data
        """
        feature_constitutions = {}

        # Extract entities once (shared across features)
        extracted_entities = self.entity_extractor.extract_entities(
            product_text, solution_text, business_model_text
        )

        for feature in detected_features:
            # Generate success criteria for this feature
            success_criteria = self.success_criteria_generator.generate_criteria(
                business_model_text, product_text, feature.title, feature.id
            )

            # Filter entities relevant to this feature
            relevant_entities = self._filter_entities_for_feature(
                extracted_entities, feature
            )

            # Prepare feature constitution data
            feature_filename = f"{feature.id}-{feature.name}.md"
            feature_data = {
                "feature_id": feature.id,
                "feature_name": feature.title,
                "version": pitch_deck.version,
                "pitch_deck_version": pitch_deck.version,
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "updated_date": datetime.now().strftime("%Y-%m-%d"),
                "upstream_constitutions": get_strategic_constitution_types(),
                "upstream_links": [],  # Will be populated later
                "user_stories": [
                    {
                        "title": feature.title,
                        "description": feature.description,
                        "priority": feature.priority,
                        "scenarios": [
                            {
                                "given": "user views feature",
                                "when": "performs action",
                                "then": "desired outcome achieved",
                            }
                        ],
                    }
                ],
                "entities": self._format_entities(relevant_entities),
                "success_criteria": self._format_success_criteria(success_criteria),
                "feature_principles": [],  # Placeholder for now
            }

            feature_constitutions[feature_filename] = feature_data

        return feature_constitutions

    def _filter_entities_for_feature(
        self, entities: list[ExtractedEntity], feature: DetectedFeature
    ) -> list[ExtractedEntity]:
        """Filter entities relevant to specific feature.

        Args:
            entities: All extracted entities
            feature: Feature to filter for

        Returns:
            List of relevant entities
        """
        # Simple keyword matching for now
        feature_keywords = set(feature.keywords + [feature.name.lower()])
        relevant = []

        for entity in entities:
            entity_name_lower = entity.name.lower()
            if any(keyword in entity_name_lower for keyword in feature_keywords):
                relevant.append(entity)

        # If no matches, return top 2-3 most common entities (User, etc.)
        if not relevant:
            common_entities = ["User", "Profile", "Account"]
            relevant = [e for e in entities if e.name in common_entities][:2]

        return relevant

    def _format_entities(self, entities: list[ExtractedEntity]) -> list[dict]:
        """Format entities for template rendering.

        Args:
            entities: List of extracted entities

        Returns:
            List of entity dictionaries
        """
        formatted = []
        for entity in entities:
            formatted.append(
                {
                    "name": entity.name,
                    "source_link": entity.source_link,
                    "rationale": entity.rationale,
                    "attribute_suggestions": entity.attribute_suggestions,
                    "constraint_suggestions": entity.constraint_suggestions,
                    "state_suggestions": entity.state_suggestions,
                    "relationships": [
                        {
                            "type": rel.type,
                            "target": rel.target,
                            "description": rel.description,
                        }
                        for rel in entity.relationships
                    ],
                }
            )
        return formatted

    def _format_success_criteria(self, criteria: list[SuccessCriterion]) -> list[dict]:
        """Format success criteria for template rendering.

        Args:
            criteria: List of success criteria

        Returns:
            List of criterion dictionaries
        """
        formatted = []
        for criterion in criteria:
            formatted_criterion = {
                "id": criterion.id,
                "text": criterion.text,
                "type": criterion.type,
                "source_link": criterion.source_link,
            }

            if criterion.type == "derived":
                formatted_criterion.update(
                    {
                        "rationale": criterion.rationale,
                        "test": criterion.test,
                    }
                )
            else:  # placeholder
                formatted_criterion.update(
                    {
                        "business_goal": criterion.business_goal,
                        "suggested_approaches": criterion.suggested_approaches,
                    }
                )

            formatted.append(formatted_criterion)

        return formatted

    def _count_statistics(
        self, strategic: dict[str, dict], features: dict[str, dict]
    ) -> DecompositionCounts:
        """Count statistics from generated constitutions.

        Args:
            strategic: Strategic constitutions
            features: Feature constitutions

        Returns:
            DecompositionCounts
        """
        counts = DecompositionCounts()
        counts.strategic_constitutions = len(strategic)
        counts.feature_constitutions = len(features)

        # Count principles
        for constitution_data in strategic.values():
            counts.total_principles += len(constitution_data["principles"])

        # Count success criteria
        for feature_data in features.values():
            for criterion in feature_data["success_criteria"]:
                if criterion["type"] == "derived":
                    counts.success_criteria_derived += 1
                else:
                    counts.success_criteria_placeholder += 1

        # Count entities
        for feature_data in features.values():
            counts.entities_extracted += len(feature_data["entities"])

        # Count traceability links (approximate)
        counts.traceability_links = (
            counts.total_principles * 2
        )  # Each principle has source link

        return counts

    def _write_constitutions(
        self, strategic: dict[str, dict], features: dict[str, dict]
    ) -> None:
        """Write constitutions to files.

        Args:
            strategic: Strategic constitutions
            features: Feature constitutions
        """
        # Create directories
        memory_dir = self.project_root / ".specify" / "memory"
        features_dir = self.project_root / ".specify" / "features"

        memory_dir.mkdir(parents=True, exist_ok=True)
        features_dir.mkdir(parents=True, exist_ok=True)

        # Render and write strategic constitutions
        strategic_template = self.jinja_env.get_template("strategic-constitution.j2")
        for filename, data in strategic.items():
            rendered = strategic_template.render(**data)
            output_path = memory_dir / filename
            output_path.write_text(rendered)

        # Render and write feature constitutions
        feature_template = self.jinja_env.get_template("feature-constitution.j2")
        for filename, data in features.items():
            rendered = feature_template.render(**data)
            output_path = features_dir / filename
            output_path.write_text(rendered)
