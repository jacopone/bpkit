#!/usr/bin/env bash
# BP-Kit Decomposition Setup
# Prepares directory structure and returns paths for AI to populate

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/bp-common.sh"

# Parse arguments
INPUT_SOURCE=""
INPUT_PATH=""
DRY_RUN=false
FEATURES_COUNT="auto"
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --interactive)
            INPUT_SOURCE="interactive"
            shift
            ;;
        --from-file)
            INPUT_SOURCE="file"
            INPUT_PATH="$2"
            shift 2
            ;;
        --from-pdf)
            INPUT_SOURCE="pdf"
            INPUT_PATH="$2"
            shift 2
            ;;
        --features)
            FEATURES_COUNT="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate input source
if [[ -z "$INPUT_SOURCE" ]]; then
    echo "ERROR: Must specify input source: --interactive, --from-file, or --from-pdf" >&2
    exit 1
fi

# Validate input file if specified
if [[ "$INPUT_SOURCE" != "interactive" && ! -f "$INPUT_PATH" ]]; then
    echo "ERROR: Input file not found: $INPUT_PATH" >&2
    exit 1
fi

# Initialize BP paths
eval "$(get_bp_paths)"

# Create directory structure if not dry run
if [[ "$DRY_RUN" == "false" ]]; then
    mkdir -p "$BP_DECK_DIR"
    mkdir -p "$BP_MEMORY_DIR"
    mkdir -p "$BP_FEATURES_DIR"
    mkdir -p "$BP_CHANGELOG_DIR"
fi

# Determine output paths
STRATEGIC_CONSTITUTIONS=(
    "$BP_MEMORY_DIR/company-constitution.md"
    "$BP_MEMORY_DIR/product-constitution.md"
    "$BP_MEMORY_DIR/market-constitution.md"
    "$BP_MEMORY_DIR/business-constitution.md"
)

# Check for existing constitutions
EXISTING_CONSTITUTIONS=false
for constitution in "${STRATEGIC_CONSTITUTIONS[@]}"; do
    if [[ -f "$constitution" ]]; then
        EXISTING_CONSTITUTIONS=true
        break
    fi
done

# Warn if constitutions already exist
if [[ "$EXISTING_CONSTITUTIONS" == "true" && "$DRY_RUN" == "false" ]]; then
    if [[ "$JSON_OUTPUT" == "false" ]]; then
        print_warning "Strategic constitutions already exist. They will be overwritten."
        if ! ask_yes_no "Continue?"; then
            echo "Aborted by user"
            exit 0
        fi
    fi
fi

# Output JSON for AI to consume
if [[ "$JSON_OUTPUT" == "true" ]]; then
    cat <<EOF
{
  "input_source": "$INPUT_SOURCE",
  "input_path": "$INPUT_PATH",
  "dry_run": $DRY_RUN,
  "features_count": "$FEATURES_COUNT",
  "paths": {
    "deck_dir": "$BP_DECK_DIR",
    "deck_file": "$BP_DECK_FILE",
    "memory_dir": "$BP_MEMORY_DIR",
    "features_dir": "$BP_FEATURES_DIR",
    "changelog_dir": "$BP_CHANGELOG_DIR",
    "templates_dir": "$BP_TEMPLATES_DIR"
  },
  "strategic_constitutions": {
    "company": "$BP_MEMORY_DIR/company-constitution.md",
    "product": "$BP_MEMORY_DIR/product-constitution.md",
    "market": "$BP_MEMORY_DIR/market-constitution.md",
    "business": "$BP_MEMORY_DIR/business-constitution.md"
  },
  "templates": {
    "pitch_deck": "$BP_TEMPLATES_DIR/pitch-deck-template.md",
    "strategic": "$BP_TEMPLATES_DIR/strategic-constitution-template.md",
    "feature": "$BP_TEMPLATES_DIR/feature-constitution-template.md"
  },
  "existing_constitutions": $EXISTING_CONSTITUTIONS,
  "next_feature_id": "$(get_next_feature_id "$BP_FEATURES_DIR")"
}
EOF
else
    print_bp_banner
    print_info "Input source: $INPUT_SOURCE"
    [[ -n "$INPUT_PATH" ]] && print_info "Input path: $INPUT_PATH"
    print_info "Deck file: $BP_DECK_FILE"
    print_info "Strategic constitutions: $BP_MEMORY_DIR/"
    print_info "Feature constitutions: $BP_FEATURES_DIR/"
    print_info "Next feature ID: $(get_next_feature_id "$BP_FEATURES_DIR")"

    if [[ "$DRY_RUN" == "true" ]]; then
        print_warning "DRY RUN: No files will be created"
    else
        print_success "Ready for decomposition"
    fi
fi

exit 0
