#!/usr/bin/env bash
# BP-Kit decomposition setup script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/bp-common.sh"

# Setup decomposition environment
setup_decompose() {
    log_info "Setting up BP-Kit decomposition environment..."
    
    # Create required directories
    mkdir -p .specify/deck
    mkdir -p .specify/features
    mkdir -p .specify/changelog
    
    log_info "BP-Kit decomposition environment ready"
}

main() {
    setup_decompose
}

main "$@"
