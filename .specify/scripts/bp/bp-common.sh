#!/usr/bin/env bash
# BP-Kit Common Utilities
# Shared functions for business plan decomposition and sync

# Source the main Speckit common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../bash/common.sh"

# BP-Kit specific paths
get_bp_paths() {
    local repo_root=$(get_repo_root)

    cat <<EOF
BP_DECK_DIR='$repo_root/.specify/deck'
BP_DECK_FILE='$repo_root/.specify/deck/pitch-deck.md'
BP_MEMORY_DIR='$repo_root/.specify/memory'
BP_FEATURES_DIR='$repo_root/.specify/features'
BP_CHANGELOG_DIR='$repo_root/.specify/changelog'
BP_TEMPLATES_DIR='$repo_root/.specify/templates'
BP_SCRIPTS_DIR='$repo_root/.specify/scripts/bp'
EOF
}

# Initialize BP paths as variables
eval "$(get_bp_paths)"

# Get next available feature ID
get_next_feature_id() {
    local features_dir="$1"
    local highest=0

    if [[ -d "$features_dir" ]]; then
        for file in "$features_dir"/*-*.md; do
            [[ -e "$file" ]] || continue
            local filename=$(basename "$file")
            if [[ "$filename" =~ ^([0-9]{3})- ]]; then
                local number=${BASH_REMATCH[1]}
                number=$((10#$number))
                if [[ "$number" -gt "$highest" ]]; then
                    highest=$number
                fi
            fi
        done
    fi

    printf "%03d" $((highest + 1))
}

# Slugify a name (convert to filename-safe format)
slugify() {
    echo "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g' | sed -E 's/^-+|-+$//g'
}

# Extract section from markdown file by ID
extract_section_by_id() {
    local file="$1"
    local section_id="$2"

    if [[ ! -f "$file" ]]; then
        echo "ERROR: File not found: $file" >&2
        return 1
    fi

    # Extract content between <a id="section-id"></a> and next heading or end
    awk -v id="$section_id" '
        /<a id="'"$section_id"'"><\/a>/ { found=1; next }
        found && /^##/ { exit }
        found { print }
    ' "$file"
}

# Get constitution version from file
get_constitution_version() {
    local file="$1"
    grep -m 1 '^\*\*Version\*\*:' "$file" | sed -E 's/.*Version\*\*:[[:space:]]*([0-9]+\.[0-9]+\.[0-9]+).*/\1/'
}

# Bump version (MAJOR.MINOR.PATCH)
bump_version() {
    local version="$1"
    local bump_type="$2"  # major, minor, or patch

    IFS='.' read -r major minor patch <<< "$version"

    case "$bump_type" in
        major)
            echo "$((major + 1)).0.0"
            ;;
        minor)
            echo "${major}.$((minor + 1)).0"
            ;;
        patch)
            echo "${major}.${minor}.$((patch + 1))"
            ;;
        *)
            echo "$version"
            ;;
    esac
}

# Create timestamp
get_timestamp() {
    date +"%Y-%m-%d"
}

# Create changelog filename
get_changelog_filename() {
    local topic="$1"
    local slug=$(slugify "$topic")
    echo "$(get_timestamp)-${slug}.md"
}

# Check if file exists and is not empty
file_exists_and_not_empty() {
    [[ -f "$1" && -s "$1" ]]
}

# Count feature constitutions
count_features() {
    local features_dir="$1"
    if [[ ! -d "$features_dir" ]]; then
        echo "0"
        return
    fi

    local count=0
    for file in "$features_dir"/*-*.md; do
        [[ -e "$file" ]] && ((count++))
    done
    echo "$count"
}

# Extract deck version from constitution metadata
get_deck_version_from_constitution() {
    local constitution_file="$1"
    grep -m 1 'Derived From Deck Version' "$constitution_file" | sed -E 's/.*Version\*\*:[[:space:]]*([0-9]+\.[0-9]+\.[0-9]+).*/\1/' | head -1
}

# Validate pitch deck has all required sections
validate_pitch_deck() {
    local deck_file="$1"
    local required_sections=(
        "company-purpose"
        "problem"
        "solution"
        "why-now"
        "market"
        "competition"
        "business-model"
        "team"
        "vision"
    )

    local missing=()
    for section in "${required_sections[@]}"; do
        if ! grep -q "id=\"$section\"" "$deck_file"; then
            missing+=("$section")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "ERROR: Missing required sections: ${missing[*]}" >&2
        return 1
    fi

    return 0
}

# Print BP-Kit banner
print_bp_banner() {
    cat <<'EOF'
╔══════════════════════════════════════════════════════════════╗
║              BP-Kit: Business Plan to Constitution           ║
║           Transform pitch decks into executable MVPs         ║
╚══════════════════════════════════════════════════════════════╝
EOF
}

# Print success message
print_success() {
    echo -e "\n✅ $1\n"
}

# Print error message
print_error() {
    echo -e "\n❌ ERROR: $1\n" >&2
}

# Print warning message
print_warning() {
    echo -e "\n⚠️  WARNING: $1\n" >&2
}

# Print info message
print_info() {
    echo -e "\nℹ️  $1\n"
}

# Ask yes/no question
ask_yes_no() {
    local question="$1"
    local default="${2:-y}"

    local prompt
    if [[ "$default" == "y" ]]; then
        prompt="$question [Y/n]: "
    else
        prompt="$question [y/N]: "
    fi

    read -p "$prompt" response
    response=${response:-$default}

    [[ "$response" =~ ^[Yy] ]]
}

# Export functions for use in other scripts
export -f get_bp_paths
export -f get_next_feature_id
export -f slugify
export -f extract_section_by_id
export -f get_constitution_version
export -f bump_version
export -f get_timestamp
export -f get_changelog_filename
export -f file_exists_and_not_empty
export -f count_features
export -f get_deck_version_from_constitution
export -f validate_pitch_deck
export -f print_bp_banner
export -f print_success
export -f print_error
export -f print_warning
export -f print_info
export -f ask_yes_no
