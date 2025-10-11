{
  description = "BP-Kit CLI - Transform business plans into executable MVP specifications";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python311;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            python
            python.pkgs.pip
          ];

          # Required for binary Python packages like pymupdf
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
          ];

          shellHook = ''
            echo "🚀 BP-Kit Development Environment"
            echo "Python: $(python --version)"
            echo ""

            # Auto-create and activate virtual environment
            if [ ! -d .venv ]; then
              echo "📦 Creating virtual environment..."
              python -m venv .venv
              echo "✓ Virtual environment created"
              echo ""
            fi

            source .venv/bin/activate
            echo "✓ Virtual environment activated (.venv)"
            echo ""

            # Check if BP-Kit is installed
            if ! pip show bpkit &>/dev/null; then
              echo "📋 Quick Start:"
              echo "  1. pip install -e .              # Install BP-Kit + dependencies"
              echo "  2. bpkit --help                  # Verify installation"
              echo "  3. bpkit decompose --help        # See decomposition options"
              echo ""
              echo "Optional:"
              echo "  pip install pymupdf>=1.23.0      # For PDF support"
            else
              echo "✓ BP-Kit installed"
              echo ""
              echo "Commands:"
              echo "  bpkit --help                     # Show help"
              echo "  bpkit decompose --interactive    # Test decomposition"
              echo "  pytest                           # Run tests (if installed)"
              echo ""
            fi
          '';
        };
      }
    );
}
