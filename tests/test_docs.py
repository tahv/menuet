from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from menuet import Model
from menuet.builders.text import Render, TextMenuBuilder

DOCS_DIRECTORY = Path(__file__).parent.parent / "docs"


@pytest.mark.parametrize(
    "fpath",
    [
        DOCS_DIRECTORY / "assets" / "config_toml.py",
        DOCS_DIRECTORY / "assets" / "config_json.py",
        DOCS_DIRECTORY / "assets" / "config_yaml.py",
        DOCS_DIRECTORY / "assets" / "config_python.py",
    ],
    ids=lambda p: p.name,
)
def test_docs_config_file_format(fpath: Path) -> None:
    local: dict[str, object] = {}
    exec(fpath.read_text(), {}, local)  # noqa: S102

    model = local["model"]
    assert isinstance(model, Model)

    text = TextMenuBuilder(model, root_menu="Example", render=Render.UTF8).build()
    assert text == dedent("""\
    Example
    ├── My App
    │   ├── Separator ───
    │   └── Sub-Menu
    │       └── Open GUI
    └── Print Hello""")
