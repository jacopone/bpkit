"""Sequoia Capital pitch deck section definitions."""

from enum import Enum


class SequoiaSectionType(str, Enum):
    """Canonical 10 sections from Sequoia Capital pitch deck template."""

    COMPANY_PURPOSE = "company-purpose"
    PROBLEM = "problem"
    SOLUTION = "solution"
    WHY_NOW = "why-now"
    MARKET_SIZE = "market-potential"
    COMPETITION = "competition"
    PRODUCT = "product"
    BUSINESS_MODEL = "business-model"
    TEAM = "team"
    FINANCIALS = "financials"

    @classmethod
    def from_title(cls, title: str) -> "SequoiaSectionType | None":
        """Map section title to SequoiaSectionType.

        Args:
            title: Section title (case-insensitive)

        Returns:
            SequoiaSectionType if matched, None otherwise

        Example:
            >>> SequoiaSectionType.from_title("Problem")
            <SequoiaSectionType.PROBLEM: 'problem'>
            >>> SequoiaSectionType.from_title("Market Size")
            <SequoiaSectionType.MARKET_SIZE: 'market-potential'>
        """
        title_lower = title.lower().strip()

        # Direct mapping for common titles
        title_map = {
            "company purpose": cls.COMPANY_PURPOSE,
            "problem": cls.PROBLEM,
            "solution": cls.SOLUTION,
            "why now": cls.WHY_NOW,
            "market size": cls.MARKET_SIZE,
            "market potential": cls.MARKET_SIZE,
            "competition": cls.COMPETITION,
            "product": cls.PRODUCT,
            "business model": cls.BUSINESS_MODEL,
            "team": cls.TEAM,
            "financials": cls.FINANCIALS,
        }

        return title_map.get(title_lower)

    def get_title(self) -> str:
        """Get human-readable title for section.

        Returns:
            Title string

        Example:
            >>> SequoiaSectionType.MARKET_SIZE.get_title()
            'Market Size'
        """
        title_map = {
            self.COMPANY_PURPOSE: "Company Purpose",
            self.PROBLEM: "Problem",
            self.SOLUTION: "Solution",
            self.WHY_NOW: "Why Now",
            self.MARKET_SIZE: "Market Size",
            self.COMPETITION: "Competition",
            self.PRODUCT: "Product",
            self.BUSINESS_MODEL: "Business Model",
            self.TEAM: "Team",
            self.FINANCIALS: "Financials",
        }
        return title_map[self]

    def get_prompts(self) -> list[str]:
        """Get clarification prompts for interactive mode.

        Returns:
            List of prompt questions for this section

        Example:
            >>> prompts = SequoiaSectionType.PROBLEM.get_prompts()
            >>> len(prompts)
            2
        """
        prompts_map = {
            self.COMPANY_PURPOSE: [
                "What is your company's core mission in one sentence?",
                "Example: 'AirBnB: Book rooms with locals, rather than hotels'",
            ],
            self.PROBLEM: [
                "What pain does your customer experience?",
                "How do customers address this issue today?",
            ],
            self.SOLUTION: [
                "How does your product make the customer's life better?",
                "What are the key use cases?",
                "Where does your product physically sit in the workflow?",
            ],
            self.WHY_NOW: [
                "What has changed recently that creates this opportunity?",
                "What trends support your business now?",
            ],
            self.MARKET_SIZE: [
                "What is your Total Addressable Market (TAM)?",
                "What is your Serviceable Available Market (SAM)?",
                "What is your Serviceable Obtainable Market (SOM)?",
                "Who is your target customer?",
            ],
            self.COMPETITION: [
                "Who are your main competitors?",
                "What are your competitive advantages?",
                "Why will you win?",
            ],
            self.PRODUCT: [
                "What is your current product offering?",
                "What features are planned for v1, v2, v3?",
                "What is on the roadmap?",
            ],
            self.BUSINESS_MODEL: [
                "How do you make money?",
                "What is your pricing model?",
                "What is the average account size or LTV?",
                "How do you distribute and sell?",
            ],
            self.TEAM: [
                "Who are the founders and what's their background?",
                "Who is on the management team?",
                "Who are your advisors or board members?",
            ],
            self.FINANCIALS: [
                "What are your revenue projections (Year 1-3)?",
                "What are your key expenses?",
                "What is your cash flow situation?",
                "How much funding are you raising?",
            ],
        }
        return prompts_map[self]


# Section-to-Constitution mapping (FR-003)
SECTION_CONSTITUTION_MAP: dict[SequoiaSectionType, str] = {
    SequoiaSectionType.COMPANY_PURPOSE: "company-constitution.md",
    SequoiaSectionType.PROBLEM: "company-constitution.md",
    SequoiaSectionType.SOLUTION: "product-constitution.md",
    SequoiaSectionType.WHY_NOW: "company-constitution.md",
    SequoiaSectionType.PRODUCT: "product-constitution.md",
    SequoiaSectionType.MARKET_SIZE: "market-constitution.md",
    SequoiaSectionType.COMPETITION: "market-constitution.md",
    SequoiaSectionType.BUSINESS_MODEL: "business-constitution.md",
    SequoiaSectionType.FINANCIALS: "business-constitution.md",
    SequoiaSectionType.TEAM: "business-constitution.md",
}


def get_constitution_type(section_type: SequoiaSectionType) -> str:
    """Get constitution filename for given section type.

    Args:
        section_type: Sequoia section type

    Returns:
        Constitution filename (e.g., 'company-constitution.md')

    Example:
        >>> get_constitution_type(SequoiaSectionType.PROBLEM)
        'company-constitution.md'
    """
    return SECTION_CONSTITUTION_MAP[section_type]


def get_strategic_constitution_types() -> list[str]:
    """Get list of all 4 strategic constitution filenames.

    Returns:
        List of constitution filenames

    Example:
        >>> constitutions = get_strategic_constitution_types()
        >>> len(constitutions)
        4
    """
    return [
        "company-constitution.md",
        "product-constitution.md",
        "market-constitution.md",
        "business-constitution.md",
    ]
