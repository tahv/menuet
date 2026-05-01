set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# List available recipes
[default]
list:
    @just --list

# Sync development environment
sync:
    uv sync --all-extras --group dev --group bpy

# Open project in neovim
nvim *args:
    uv run -- nvim {{ args }}

# Build Python wheel and sdist
build:
    uv build --no-sources --clear --no-create-gitignore
    uvx check-wheel-contents dist/*.whl

# Run test suite
[group('test')]
test *args:
    uv run -m pytest {{ args }}

# Run test suite and report coverage
[group('test')]
coverage *args:
    uv run -m coverage erase
    uv run -m coverage run --parallel -m pytest {{ args }}
    uv run -m coverage combine
    uv run -m coverage report

# Serve documentation on http://127.0.0.1:8000
serve:
  uv run -m zensical serve

# Build documentation
docs:
  uv run zensical build --clean

# Create a news fragment
news filename="":
    uvx towncrier create --no-edit {{ filename }}

# Build changelog from news fragments, or print a draft if `version` is not set
changelog version="":
    uvx towncrier build {{ if version == "" { "--draft --version main" } else { "--version " + version } }}

# Ouptut release notes from `CHANGELOG.md` for `version`
hed version:
    @uvx hed --tag {{ version }}

# Generate '.github/README.md'
github-readme:
    uv run scripts/github-readme.py > .github/README.md

# Run `ruff` linter
ruff *files:
  uvx ruff@latest check --output-format concise {{files}}

# Dry run `ruff` formatter and output diff
fmt:
  uvx ruff@latest format --check
