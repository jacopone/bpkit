# Data Model: BP-Kit Quality Commands

**Feature**: BP-Kit Quality Commands (`/bp.clarify`, `/bp.analyze`, `/bp.checklist`)
**Purpose**: Define entities for quality validation, link checking, and clarification workflows

---

## Core Entities

### 1. PitchDeck

**Purpose**: Represents the pitch deck document with sections and version metadata

```yaml
PitchDeck:
  attributes:
    file_path: Path                    # .specify/deck/pitch-deck.md
    version: str                       # Semantic version (1.0.0)
    sections: List[PitchDeckSection]   # Parsed sections
    last_modified: datetime

  methods:
    parse() -> PitchDeck               # Parse markdown into sections
    get_section(section_id: str) -> PitchDeckSection | None
    update_section(section_id: str, content: str) -> None
    bump_version(bump_type: str) -> str  # MAJOR, MINOR, PATCH

  validations:
    - version MUST follow semantic versioning (X.Y.Z)
    - file_path MUST be absolute path
    - sections MUST include required Sequoia template sections
```

---

### 2. PitchDeckSection

**Purpose**: Individual section within pitch deck (e.g., #problem, #solution, #competition)

```yaml
PitchDeckSection:
  attributes:
    section_id: str                    # company-purpose, problem, solution, etc.
    title: str                         # Human-readable title
    content: str                       # Markdown content
    line_start: int                    # Line number where section begins
    line_end: int                      # Line number where section ends
    is_complete: bool                  # Whether section has meaningful content
    vague_indicators: List[str]        # Detected vague phrases

  methods:
    is_empty() -> bool                 # Check if section has only placeholders
    detect_vagueness() -> List[str]    # Find "TBD", "[X]", etc.
    get_word_count() -> int

  validations:
    - section_id MUST match Sequoia template IDs
    - content MUST be non-empty string
    - line_start MUST be < line_end
```

---

### 3. Constitution

**Purpose**: Strategic or feature constitution document with principles and links

```yaml
Constitution:
  attributes:
    file_path: Path                    # e.g., .specify/memory/company-constitution.md
    constitution_type: ConstitutionType  # STRATEGIC or FEATURE
    name: str                          # company-constitution, 001-user-management
    version: str                       # Semantic version
    principles: List[Principle]        # Constitutional principles
    upstream_links: List[TraceabilityLink]  # Links to pitch deck
    downstream_links: List[TraceabilityLink]  # Links from features

  relationships:
    - Strategic constitution has_many feature constitutions
    - Feature constitution belongs_to strategic constitutions

  methods:
    parse() -> Constitution
    validate_links() -> List[LinkValidationError]
    get_principle(principle_id: str) -> Principle | None

  validations:
    - constitution_type MUST be STRATEGIC or FEATURE
    - version MUST follow semantic versioning
    - STRATEGIC constitutions MUST link to pitch deck
    - FEATURE constitutions MUST link to strategic constitutions
```

---

### 4. Principle

**Purpose**: Individual constitutional principle with traceability

```yaml
Principle:
  attributes:
    principle_id: str                  # principle-1, principle-2, FP1, FP2
    title: str                         # Brief principle name
    rule: str                          # What MUST or MUST NOT happen
    source_link: TraceabilityLink      # Link to upstream source
    test_criteria: str                 # How to verify compliance

  methods:
    is_testable() -> bool              # Check if test criteria is specific
    has_valid_source() -> bool         # Validate source link exists

  validations:
    - principle_id MUST be unique within constitution
    - rule MUST contain "MUST" or "MUST NOT"
    - source_link MUST be valid TraceabilityLink
```

---

### 5. TraceabilityLink

**Purpose**: Reference from one document/section to another

```yaml
TraceabilityLink:
  attributes:
    source_file: Path                  # File containing the link
    source_line: int                   # Line number of link
    target_file: Path                  # Referenced file
    target_section: str                # Section ID (e.g., #principle-1)
    link_text: str                     # Display text in markdown
    link_type: LinkType                # PITCH_TO_STRATEGIC, STRATEGIC_TO_FEATURE, etc.

  methods:
    validate() -> LinkValidationResult # Check if target exists
    get_target() -> str | None         # Resolve target content

  validations:
    - source_file MUST exist
    - target_file MUST exist
    - target_section MUST exist in target_file if specified
    - link_type MUST be valid enum value

  states:
    VALID: Target file and section both exist
    BROKEN_FILE: Target file does not exist
    BROKEN_SECTION: Target file exists but section does not
    MISSING_SOURCE: Source file does not exist
```

---

### 6. ClarificationQuestion

**Purpose**: Represents an ambiguity requiring user input

```yaml
ClarificationQuestion:
  attributes:
    question_id: str                   # CLQ001, CLQ002, etc.
    question_text: str                 # "Who are your top 3 competitors?"
    section_id: str                    # Which pitch deck section
    priority: Priority                 # HIGH, MEDIUM, LOW
    suggested_answers: List[str]       # Pre-populated options
    user_answer: str | None            # User's response

  methods:
    ask_interactively() -> str         # Prompt user for answer
    update_pitch_deck(deck: PitchDeck) -> None  # Write answer to section

  validations:
    - question_text MUST be non-empty
    - section_id MUST reference valid pitch deck section
    - priority MUST be HIGH, MEDIUM, or LOW
    - suggested_answers list MUST have at least 2 options
```

---

### 7. AnalysisReport

**Purpose**: Results from `/bp.analyze` validation

```yaml
AnalysisReport:
  attributes:
    report_id: str                     # Unique ID
    timestamp: datetime
    pitch_deck_version: str            # Version analyzed
    constitutions_analyzed: int        # Count of constitutions checked
    errors: List[ValidationError]      # Blocking issues
    warnings: List[ValidationWarning]  # Non-blocking issues
    info: List[ValidationInfo]         # Informational notes

  methods:
    has_errors() -> bool
    has_warnings() -> bool
    is_passing() -> bool               # True if no errors
    format_summary() -> str            # Human-readable report
    save_to_changelog() -> Path        # Write to .specify/changelog/

  validations:
    - errors, warnings, info MUST be sorted by severity
    - timestamp MUST be ISO 8601 format
```

---

### 8. ValidationError / ValidationWarning / ValidationInfo

**Purpose**: Specific issues found during analysis

```yaml
ValidationIssue:  # Base class
  attributes:
    issue_id: str                      # ERR001, WARN001, INFO001
    severity: Severity                 # ERROR, WARNING, INFO
    message: str                       # Human-readable description
    file_path: Path                    # Affected file
    line_number: int | None            # Specific line if applicable
    suggestion: str                    # How to fix

  subtypes:
    - BrokenLinkError: Link target does not exist
    - ConflictError: Contradictory principles detected
    - CoverageWarning: Pitch deck section not referenced
    - VersionMismatchWarning: Constitution references old pitch deck version
    - OrphanedPrincipleInfo: Principle has no downstream references

  methods:
    format() -> str                    # Console-friendly output
    get_context() -> str               # Show surrounding lines

  validations:
    - severity MUST match issue type (ERROR for BrokenLink, etc.)
    - file_path MUST exist
    - line_number MUST be positive if provided
```

---

### 9. ChecklistItem

**Purpose**: Individual validation criterion in a quality checklist

```yaml
ChecklistItem:
  attributes:
    item_id: str                       # CHK001, CHK002, etc.
    description: str                   # "All principles have measurable outcomes"
    is_checked: bool                   # User has validated this
    category: str                      # "Traceability", "Completeness", "Quality"
    applies_to: ConstitutionType       # STRATEGIC, FEATURE, or BOTH

  methods:
    to_markdown() -> str               # Convert to "- [ ] description"
    check() -> None                    # Mark as completed
    uncheck() -> None                  # Mark as incomplete

  validations:
    - item_id MUST be unique within checklist
    - description MUST be specific and actionable
    - applies_to MUST be valid ConstitutionType or BOTH
```

---

### 10. Checklist

**Purpose**: Collection of checklist items for a constitution

```yaml
Checklist:
  attributes:
    checklist_id: str                  # Unique ID
    constitution_file: Path            # Target constitution
    items: List[ChecklistItem]         # Validation items
    completion_percentage: float       # 0.0 to 100.0
    last_updated: datetime

  methods:
    calculate_completion() -> float    # Count checked / total
    add_item(item: ChecklistItem) -> None
    parse_from_file(path: Path) -> Checklist  # Read existing checklist
    save_to_file(path: Path) -> None   # Write checklist markdown

  validations:
    - items list MUST have at least 5 items
    - completion_percentage MUST be 0.0 to 100.0
    - constitution_file MUST exist
```

---

## Enumerations

### ConstitutionType
```python
class ConstitutionType(Enum):
    STRATEGIC = "strategic"  # company, product, market, business
    FEATURE = "feature"      # feature constitutions (001-XXX.md)
```

### LinkType
```python
class LinkType(Enum):
    PITCH_TO_STRATEGIC = "pitch_to_strategic"      # Deck → Strategic constitution
    STRATEGIC_TO_PITCH = "strategic_to_pitch"      # Strategic → Deck (reverse)
    STRATEGIC_TO_FEATURE = "strategic_to_feature"  # Strategic → Feature constitution
    FEATURE_TO_STRATEGIC = "feature_to_strategic"  # Feature → Strategic (reverse)
    FEATURE_TO_PITCH = "feature_to_pitch"          # Feature → Deck (direct)
```

### Priority
```python
class Priority(Enum):
    HIGH = "high"      # Scope-impacting, financial, security
    MEDIUM = "medium"  # Strategy, user experience
    LOW = "low"        # Details, polish, nice-to-have
```

### Severity
```python
class Severity(Enum):
    ERROR = "error"      # Blocks progression, must fix
    WARNING = "warning"  # Non-blocking, should fix
    INFO = "info"        # Informational, no action needed
```

---

## Entity Relationships

```
PitchDeck
  ├─ has_many → PitchDeckSection
  ├─ referenced_by → Constitution (strategic)
  └─ version_tracked_by → Constitution.upstream_links

Constitution (Strategic)
  ├─ has_many → Principle
  ├─ links_to → PitchDeck (via TraceabilityLink)
  ├─ referenced_by → Constitution (feature)
  └─ validated_by → Checklist

Constitution (Feature)
  ├─ has_many → Principle
  ├─ links_to → Constitution (strategic)
  ├─ links_to → PitchDeck (optional direct links)
  └─ validated_by → Checklist

TraceabilityLink
  ├─ belongs_to → Constitution (source)
  ├─ references → Constitution | PitchDeck (target)
  └─ validated_by → AnalysisReport

ClarificationQuestion
  ├─ belongs_to → PitchDeckSection
  └─ updates → PitchDeck (when answered)

AnalysisReport
  ├─ analyzes → PitchDeck
  ├─ analyzes → Constitution (many)
  └─ contains → ValidationError/Warning/Info (many)

Checklist
  ├─ validates → Constitution
  ├─ contains → ChecklistItem (many)
  └─ tracked_by → completion_percentage
```

---

## State Machines

### TraceabilityLink Validation States

```
[CREATED] --validate()--> [VALID] | [BROKEN_FILE] | [BROKEN_SECTION] | [MISSING_SOURCE]

Transitions:
- CREATED → VALID: Target file and section both exist
- CREATED → BROKEN_FILE: target_file does not exist
- CREATED → BROKEN_SECTION: target_file exists but target_section missing
- CREATED → MISSING_SOURCE: source_file does not exist

Recovery:
- BROKEN_FILE: User creates missing file or updates link
- BROKEN_SECTION: User adds missing section or updates link
- MISSING_SOURCE: Error (should never happen if parsing succeeded)
```

### ClarificationQuestion States

```
[CREATED] --ask_interactively()--> [ANSWERED] --update_pitch_deck()--> [APPLIED]

Transitions:
- CREATED → ANSWERED: User provides answer (user_answer populated)
- ANSWERED → APPLIED: Answer written to pitch deck, version bumped

Cancellation:
- CREATED → SKIPPED: User chooses not to answer (optional questions)
```

### Checklist Completion States

```
[EMPTY] --add_items()--> [INCOMPLETE] --check_items()--> [COMPLETE]

Transitions:
- EMPTY → INCOMPLETE: Items added, completion_percentage = 0%
- INCOMPLETE → INCOMPLETE: Some items checked, 0% < completion < 100%
- INCOMPLETE → COMPLETE: All items checked, completion_percentage = 100%

Regression:
- COMPLETE → INCOMPLETE: User unchecks an item
```

---

## Usage Examples

### Example 1: `/bp.clarify` Workflow

```python
# 1. Parse pitch deck
deck = PitchDeck.parse(".specify/deck/pitch-deck.md")

# 2. Detect vague sections
questions = []
for section in deck.sections:
    if section.is_empty() or section.detect_vagueness():
        question = ClarificationQuestion(
            question_id=f"CLQ{len(questions)+1:03d}",
            question_text=generate_question(section),
            section_id=section.section_id,
            priority=determine_priority(section),
            suggested_answers=[...]
        )
        questions.append(question)

# 3. Ask questions (max 5, prioritized)
questions.sort(key=lambda q: q.priority, reverse=True)
for question in questions[:5]:
    answer = question.ask_interactively()
    question.update_pitch_deck(deck)

# 4. Bump version and save
deck.bump_version("PATCH")
```

### Example 2: `/bp.analyze` Workflow

```python
# 1. Parse all constitutions
deck = PitchDeck.parse(".specify/deck/pitch-deck.md")
strategic = [Constitution.parse(f) for f in glob(".specify/memory/*.md")]
features = [Constitution.parse(f) for f in glob(".specify/features/*.md")]

# 2. Validate all links
report = AnalysisReport(timestamp=now())
for constitution in strategic + features:
    errors = constitution.validate_links()
    report.errors.extend(errors)

# 3. Detect conflicts
conflicts = detect_conflicts(strategic)
report.warnings.extend(conflicts)

# 4. Check coverage
coverage_gaps = check_coverage(deck, strategic)
report.warnings.extend(coverage_gaps)

# 5. Display report
print(report.format_summary())
report.save_to_changelog()
```

### Example 3: `/bp.checklist` Workflow

```python
# 1. Load constitutions
constitutions = [
    Constitution.parse(f)
    for f in glob(".specify/memory/*.md") + glob(".specify/features/*.md")
]

# 2. Generate checklists
for constitution in constitutions:
    checklist = Checklist(
        checklist_id=f"CL-{constitution.name}",
        constitution_file=constitution.file_path,
        items=generate_checklist_items(constitution)
    )

    output_path = f".specify/checklists/{constitution.name}.md"
    checklist.save_to_file(output_path)

# 3. Report generation (--report flag)
for checklist_file in glob(".specify/checklists/*.md"):
    checklist = Checklist.parse_from_file(checklist_file)
    completion = checklist.calculate_completion()
    print(f"{checklist.constitution_file.name}: {completion:.0f}% complete")
```

---

## Constraints & Validations

1. **File Path Constraints**:
   - All file paths MUST be absolute
   - Pitch deck MUST be at `.specify/deck/pitch-deck.md`
   - Strategic constitutions MUST be in `.specify/memory/`
   - Feature constitutions MUST be in `.specify/features/`
   - Checklists MUST be in `.specify/checklists/`

2. **Version Constraints**:
   - All versions MUST follow semantic versioning (X.Y.Z)
   - Version comparisons MUST use semver parsing (not string comparison)
   - Version bumps MUST follow rules: MAJOR (breaking), MINOR (additive), PATCH (fixes)

3. **Link Constraints**:
   - Markdown links MUST use relative paths from file location
   - Section IDs MUST match actual heading IDs in target file
   - Broken links MUST be reported as ERROR severity
   - Circular references MUST be detected and reported as WARNING

4. **Question Constraints**:
   - Maximum 5 clarification questions per `/bp.clarify` run
   - Questions MUST be prioritized by impact (HIGH > MEDIUM > LOW)
   - Each question MUST provide at least 2 suggested answers

5. **Checklist Constraints**:
   - Strategic constitution checklists MUST have at least 10 items
   - Feature constitution checklists MUST have at least 15 items
   - Checklist items MUST be actionable and specific
   - Completion percentage MUST be recalculated on every parse

---

## Performance Considerations

- **Lazy Loading**: Parse constitutions only when needed (not all at once)
- **Caching**: Cache parsed documents during single command execution
- **Parallel Validation**: Validate links in parallel using asyncio
- **Efficient Parsing**: Use markdown-it-py's token stream (don't render HTML)
- **Index Section IDs**: Build section ID index once per file for O(1) lookup

Target performance:
- Parse single constitution: <50ms
- Validate all links (10 constitutions): <500ms
- Generate all checklists: <200ms
- Full `/bp.analyze` run: <2 seconds

---

**Version**: 1.0.0
**Created**: 2025-10-10
**Last Updated**: 2025-10-10
