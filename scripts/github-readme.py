# /// script
# dependencies = []
# ///
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

HEADER = """\
> [!IMPORTANT]
> Development takes place on GitLab:
> [gitlab.com/tahv/menuet](https://gitlab.com/tahv/menuet).

"""


def main(args: Sequence[str] | None = None) -> None:
    """Command line entry point."""
    parser = argparse.ArgumentParser(description="Generate '.github/README.md'")
    parser.add_argument(
        "readme",
        nargs="?",
        default="README.md",
        help="Project README.md",
    )
    namespace = parser.parse_args(args)

    readme = Path(namespace.readme)
    if not readme.is_file():
        raise FileNotFoundError(readme)

    print(f"{HEADER}{readme.read_text()}", file=sys.stdout, end="")


if __name__ == "__main__":
    main()
