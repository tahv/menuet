from __future__ import annotations

import io
from pathlib import Path
from textwrap import dedent

import copykitten
import pytest

from menuet import load
from menuet.action import Action
from menuet.menu import Menu
from menuet.model import ItemAction, ItemGroup, ItemMenu, Model, loads
from menuet.utils import passthrough

# TODO(tga): def test_parse_action_cb_url() -> None:


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        pytest.param(
            """\
            [[action]]
            id = "test"
            cb = 'print("Hello World")'
            """,
            "Hello World\n",
            id="no-scheme",
        ),
        pytest.param(
            """\
            [[action]]
            id = "test"
            cb = 'exec:print("Hello World")'
            """,
            "Hello World\n",
            id="scheme",
        ),
        pytest.param(
            '''\
            [[action]]
            id = "test"
            cb = """
            print("Hello")
            print("World")
            """
            ''',
            "Hello\nWorld\n",
            id="no-scheme-multiline",
        ),
        pytest.param(
            '''\
            [[action]]
            id = "test"
            cb = """exec:
            print("Hello")
            print("World")
            """
            ''',
            "Hello\nWorld\n",
            id="scheme-multiline",
        ),
    ],
)
def test_parse_action_cb_exec(
    config: str,
    expected: str,
    capfd: pytest.CaptureFixture[str],
) -> None:
    model = Model()
    loads(dedent(config), model)
    action = model.get_action("test")
    action.cb()
    assert capfd.readouterr().out == expected


def test_parse_action_cb_copy() -> None:
    model = Model()
    loads(
        dedent("""\
        [[action]]
        id = "test"
        cb = 'copy:Hello World'
        """),
        model,
    )
    action = model.get_action("test")
    action.cb()
    assert copykitten.paste() == "Hello World"


def test_parse_action_no_cb() -> None:
    model = Model()
    loads(
        dedent("""\
        [[action]]
        id = "test"
        """),
        model,
    )
    action = model.get_action("test")
    assert action.cb is passthrough


def test_parse_action_cp_ep(capfd: pytest.CaptureFixture[str]) -> None:
    model = Model()
    loads(
        dedent("""\
        [[action]]
        id = "test"
        cb = "ep:tests.data.ep:print_hello"
        """),
        model,
    )
    action = model.get_action("test")
    action.cb()
    assert capfd.readouterr().out == "Hello World !\n"


def test_parse_action_label() -> None:
    model = Model()
    loads(
        dedent("""\
        [[action]]
        id = "test"
        label = "Test Label"
        """),
        model,
    )
    action = model.get_action("test")
    assert action.label == "Test Label"


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        pytest.param(
            'action = [{ id = "test", desc = "Test Description"}]',
            "Test Description",
            id="set",
        ),
        pytest.param(
            'action = [{ id = "test"}]',
            None,
            id="default",
        ),
    ],
)
def test_parse_action_desc(config: str, expected: str | None) -> None:
    model = Model()
    loads(dedent(config), model)
    action = model.get_action("test")
    assert action.desc == expected


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        pytest.param(
            'action = [{ id = "test", group = "Test Group"}]',
            "Test Group",
            id="set",
        ),
        pytest.param(
            'action = [{ id = "test"}]',
            None,
            id="default",
        ),
    ],
)
def test_parse_action_group(config: str, expected: str | None) -> None:
    model = Model()
    loads(dedent(config), model)
    action = model.get_action("test")
    assert action.group == expected


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        pytest.param(
            'action = [{ id = "test", icon = "tests/data/circle.svg" }]',
            Action(id="test", icon=Path("tests/data/circle.svg")),
            id="no-scheme",
        ),
        pytest.param(
            'action = [{ id = "test", icon = "path:tests/data/circle.svg" }]',
            Action(id="test", icon=Path("tests/data/circle.svg")),
            id="scheme-path",
        ),
        pytest.param(
            'action = [{ id = "test", icon = "res:tests.data:circle.svg" }]',
            Action(id="test", icon=Path("tests/data/circle.svg").absolute()),
            id="scheme-res",
        ),
    ],
)
def test_parse_action_icon(config: str, expected: Action) -> None:
    model = Model()
    loads(dedent(config), model)
    action = model.get_action(expected.id)
    assert action == expected


def test_model_parse_raise_action_exist() -> None:
    model = Model()
    with pytest.raises(ValueError, match=r"Action 'test' already exists in model"):
        loads(
            dedent("""\
            [[action]]
            id = "test"
            [[action]]
            id = "test"
            """),
            model,
        )


def test_model_parse_raise_menu_exist() -> None:
    model = Model()
    with pytest.raises(
        ValueError,
        match=r"Menu \('Test',\) already exists in model",
    ):
        loads(
            dedent("""\
            [[menu]]
            label = "Test"
            [[menu]]
            label = "Test"
            """),
            model,
        )


def test_parse_complex_model() -> None:
    model = Model()
    loads(
        dedent("""\
        [[menu]]
        label = "Menu A"

        [[menu]]
        label = "Menu B"
        group = "Group A"

        [[menu]]
        menu = ["Menu A"]
        label = "Menu C"

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

    assert list(model.iter(recursive=True)) == [
        ItemMenu(Menu(label="Menu A")),
        ItemMenu(Menu(label="Menu C", menu=("Menu A",))),
        ItemAction(Action(id="action-d", label="Action D", menu=("Menu A", "Menu C"))),
        ItemGroup("Group A", menu=()),
        ItemMenu(Menu(label="Menu B", group="Group A")),
        ItemAction(Action(id="action-b", label="Action B", menu=("Menu B",))),
        ItemGroup("Group B", menu=("Menu B",)),
        ItemAction(
            Action(id="action-c", label="Action C", menu=("Menu B",), group="Group B"),
        ),
        ItemAction(Action(id="action-a", label="Action A", group="Group A")),
    ]


def test_load_fp() -> None:
    wrapper = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    wrapper.write(
        dedent("""\
        [[action]]
        id = "test"
        label = "Test Label"
        """),
    )
    wrapper.seek(0, 0)

    model = Model()
    load(wrapper.buffer, model)
    action = model.get_action("test")
    assert action.label == "Test Label"


def test_menu_is_configured() -> None:
    assert Menu(label="Test").is_configured() is False
    assert Menu(label="Test", menu=("Parent",)).is_configured() is False
    assert Menu(label="Test", group="Test Group").is_configured() is True
    assert Menu(label="Test", icon="test/icon.png").is_configured() is True
    assert Menu(label="Test", desc="Test Description").is_configured() is True
