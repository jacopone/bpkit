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
        pythonPackages = python.pkgs;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python
            pythonPackages.pip
            pythonPackages.setuptools
            pythonPackages.wheel

            # BP-Kit dependencies
            pythonPackages.typer
            pythonPackages.rich
            pythonPackages.httpx
            pythonPackages.platformdirs
            pythonPackages.readchar
            pythonPackages.pydantic
            pythonPackages.pyyaml
            pythonPackages.tenacity
            pythonPackages.markdown-it-py
            pythonPackages.jinja2

            # PDF support (optional)
            pythonPackages.pymupdf

            # Development tools
            pythonPackages.pytest
            pythonPackages.pytest-cov
            pythonPackages.black
            pythonPackages.ruff
            pythonPackages.mypy
          ];

          shellHook = ''
            echo "🚀 BP-Kit Development Environment"
            echo "Python: $(python --version)"
            echo ""
            echo "Available commands:"
            echo "  python -m bpkit_cli --help    # Run BP-Kit directly"
            echo "  pytest                         # Run tests"
            echo "  black src/                     # Format code"
            echo "  ruff check src/                # Lint code"
            echo ""
            echo "To install in editable mode:"
            echo "  pip install -e ."
            echo ""
          '';
        };

        packages.default = pythonPackages.buildPythonPackage {
          pname = "bpkit-cli";
          version = "0.1.0";

          src = ./.;

          format = "pyproject";

          nativeBuildInputs = with pythonPackages; [
            hatchling
          ];

          propagatedBuildInputs = with pythonPackages; [
            typer
            rich
            httpx
            platformdirs
            readchar
            pydantic
            pyyaml
            tenacity
            markdown-it-py
            jinja2
          ];

          pythonImportsCheck = [ "bpkit_cli" ];

          meta = with pkgs.lib; {
            description = "Transform business plans into executable MVP specifications";
            homepage = "https://github.com/yourusername/bp-kit";
            license = licenses.mit;
            maintainers = [ ];
          };
        };
      }
    );
}
