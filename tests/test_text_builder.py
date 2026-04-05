from __future__ import annotations

from textwrap import dedent

import pytest

from menuet.builders.text import Render, TextMenuBuilder
from menuet.model import Model, loads


@pytest.mark.parametrize(
    ("render", "root", "expected"),
    [
        pytest.param(
            Render.UTF8,
            "Test Menu",
            """\
            Test Menu
            ├── Menu A
            │   └── Menu C
            │       └── Action D
            ├── Group A ───
            ├── Menu B
            │   ├── Action B
            │   ├── Group B ───
            │   └── Action C
            └── Action A
            """,
            id="utf8-root",
        ),
        pytest.param(
            Render.UTF8,
            None,
            """\
            Menu A
            └── Menu C
                └── Action D
            Group A ───
            Menu B
            ├── Action B
            ├── Group B ───
            └── Action C
            Action A
            """,
            id="utf8-no-root",
        ),
        pytest.param(
            Render.ASCII,
            "Test Menu",
            """\
            Test Menu
            |-- Menu A
            |   `-- Menu C
            |       `-- Action D
            |-- Group A ---
            |-- Menu B
            |   |-- Action B
            |   |-- Group B ---
            |   `-- Action C
            `-- Action A
            """,
            id="ascii-root",
        ),
        pytest.param(
            Render.ASCII,
            None,
            """\
            Menu A
            `-- Menu C
                `-- Action D
            Group A ---
            Menu B
            |-- Action B
            |-- Group B ---
            `-- Action C
            Action A
            """,
            id="ascii-no-root",
        ),
    ],
)
def test_text_menu_builder(
    render: Render,
    root: str | None,
    expected: str,
) -> None:
    model = Model()
    loads(
        dedent("""\
        [[menu]]
        label = "Menu B"
        group = "Group A"

        [[action]]
        id = "action-a"
        label = "Action A"
        group = "Group A"

        [[action]]
        id = "action-b"
        menu = ["Menu B"]
        label = "Action B"

        [[action]]
        id = "action-c"
        menu = ["Menu B"]
        label = "Action C"
        group = "Group B"

        [[action]]
        id = "action-d"
        menu = ["Menu A", "Menu C"]
        label = "Action D"
        """),
        model,
    )

    builder = TextMenuBuilder(model, render=render, root_menu=root)
    assert builder.build() == dedent(expected).rstrip()
