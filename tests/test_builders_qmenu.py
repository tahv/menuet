from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QMenu

from menuet.builders.qt import QMenuBuilder
from menuet.model import Model, loads

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


def test_qmenu_builder(qtbot: QtBot) -> None:
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
        icon = "res:tests.data:circle.svg"

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

    builder = QMenuBuilder(model, root_menu="Test Menu")
    qmenu = builder.build()
    qtbot.add_widget(qmenu)

    assert qmenu.title() == "Test Menu"

    qmenu_a = qmenu.actions()[0].menu()
    assert isinstance(qmenu_a, QMenu)
    assert qmenu_a.title() == "Menu A"

    qmenu_c = qmenu_a.actions()[0].menu()
    assert isinstance(qmenu_c, QMenu)
    assert qmenu_c.title() == "Menu C"

    assert qmenu_c.actions()[0].text() == "Action D"

    assert qmenu.actions()[1].text() == "Group A"

    qmenu_b = qmenu.actions()[2].menu()
    assert isinstance(qmenu_b, QMenu)
    assert qmenu_b.title() == "Menu B"

    assert qmenu_b.actions()[0].text() == "Action B"
    assert qmenu_b.actions()[1].text() == "Group B"
    assert qmenu_b.actions()[2].text() == "Action C"

    assert qmenu.actions()[3].text() == "Action A"
    assert not qmenu.actions()[3].icon().isNull()


def test_qmenu_builder_returns_qmenu_instance(qtbot: QtBot) -> None:
    model = Model()
    builder = QMenuBuilder(model, root_menu="Test Menu")
    qmenu = builder.build()
    qtbot.add_widget(qmenu)

    assert isinstance(qmenu, QMenu)


def test_qmenu_builder_set_qactions_label(qtbot: QtBot) -> None:
    model = Model()
    loads(
        dedent("""\
        [[action]]
        id = "test"
        label = "Test Action"
        """),
        model,
    )
    builder = QMenuBuilder(model, root_menu="Test Menu")
    qmenu = builder.build()
    qtbot.add_widget(qmenu)

    assert len(qmenu.actions()) == 1
    assert qmenu.actions()[0].text() == "Test Action"


def test_qmenu_builder_set_qactions_icon(qtbot: QtBot) -> None:
    model = Model()
    loads(
        dedent("""\
        [[action]]
        id = "test"
        icon = "res:tests.data:circle.svg"
        """),
        model,
    )
    builder = QMenuBuilder(model, root_menu="Test Menu")
    qmenu = builder.build()
    qtbot.add_widget(qmenu)

    assert len(qmenu.actions()) == 1
    assert not qmenu.actions()[0].icon().isNull()


def test_qmenu_builder_set_qactions_tooltip(qtbot: QtBot) -> None:
    model = Model()
    loads(
        dedent("""\
        [[action]]
        id = "test"
        desc = "Test Description"
        """),
        model,
    )
    builder = QMenuBuilder(model, root_menu="Test Menu")
    qmenu = builder.build()
    qtbot.add_widget(qmenu)

    assert len(qmenu.actions()) == 1
    assert qmenu.actions()[0].toolTip() == "Test Description"


def test_qmenu_builder_insert_dummy_separator_first(qtbot: QtBot) -> None:
    model = Model()
    loads(
        dedent("""\
        [[action]]
        id = "test"
        label = "Test Action"
        group = "Test Group"
        """),
        model,
    )
    builder = QMenuBuilder(model, root_menu="Test Menu")
    qmenu = builder.build()
    qtbot.add_widget(qmenu)

    assert len(qmenu.actions()) == 3
    assert qmenu.actions()[0].text() == ""
    assert qmenu.actions()[1].text() == "Test Group"
    assert qmenu.actions()[2].text() == "Test Action"


def test_qmenu_builder_under_existing_qmenu(qtbot: QtBot) -> None:
    existing_qmenu = QMenu("Test Menu")
    qtbot.add_widget(existing_qmenu)
    existing_qmenu.addAction("Existing Action")

    model = Model()
    loads(
        dedent("""\
        [[action]]
        id = "test"
        label = "Test Action"
        """),
        model,
    )
    builder = QMenuBuilder(model, root_menu=existing_qmenu)
    qmenu = builder.build()
    qtbot.add_widget(existing_qmenu)

    assert qmenu == existing_qmenu

    assert len(qmenu.actions()) == 1
    assert qmenu.actions()[0].text() == "Test Action"
