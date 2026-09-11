set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

check-wheel-contents := "uvx check-wheel-contents@0.6.3"
creosote := "uvx creosote@5.2.0"
hatch := "uvx hatch@1.18.0"
hed := "uvx hed@1.3.0"
ruff := "uvx ruff@0.16.6"
towncrier := "uvx towncrier@25.8.0"
uvbump := "uvx --from git+https://github.com/Rezarys/uvbump@3f33228 uvbump"

# List available recipes
[default]
list:
    @just --list --list-heading "" --list-prefix ""

# Sync development environment
sync:
    uv sync --all-extras --group dev --group bpy

# Open project in neovim
nvim *args:
    uv run -- nvim {{ args }}

# Build Python wheel and sdist
build:
    uv build --no-sources --clear --no-create-gitignore
    {{ check-wheel-contents }} dist/*.whl

# Run test suite
test *args:
    uv run -m pytest {{ args }}

# Run test suite and report coverage
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
    {{ towncrier }} create --no-edit {{ filename }}

# Build changelog from news fragments, or print a draft if `version` is not set
changelog version="":
    {{ towncrier }} build {{ if version == "" { "--draft --version main" } else { "--version " + version } }}

# Print release notes from `CHANGELOG.md` for `version`
hed version:
    @{{ hed }} --tag {{ version }}

# Print project version
version:
    @{{ hatch }} version

# Update project dependencies
update:
    @{{ uvbump }} --index-url https://pypi.org/simple

# Identify unused dependencies
creosote:
    @{{ creosote }}

# Generate `.github/README.md`
[script("uv", "run", "--script")]
github-readme:
    import sys, pathlib
    header = """\
    > [!IMPORTANT]
    > Development takes place on GitLab:
    > [gitlab.com/tahv/menuet](https://gitlab.com/tahv/menuet).

    """
    body = pathlib.Path('README.md').read_text()
    pathlib.Path(".github/README.md").write_text(f"{header}{body}")

# Run `ruff` linter
ruff *files:
    {{ ruff }} check --output-format concise {{ files }}

# Dry run `ruff` formatter and output diff
fmt:
    {{ ruff }} format --check

# Perform type-checking with `mypy`
mypy:
    uv run -m mypy
