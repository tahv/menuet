from __future__ import annotations

from functools import reduce
from unittest.mock import Mock

import bpy
import pytest

from menuet import Action, ItemAction, ItemMenu, Menu
from menuet.builders.blender import BlenderMenuBuilder
from menuet.demo import demo_model
from menuet.model import Model

# TODO(tga): def test_blender_build_operator_icon() -> None: ...
# TODO(tga): def test_blender_build_menu_icon() -> None: ...


@pytest.mark.parametrize(
    ("label", "expected"),
    [pytest.param("Label", "Label"), (None, "test")],
)
def test_builder_set_operator_label(label: str, expected: str) -> None:
    model = Model()
    model.add_action(Action(id="test", label=label))

    builder = BlenderMenuBuilder(model, root_menu="Test Menu")
    builder.build()

    operator = builder.find_operator(model.get_action("test").id)
    assert operator is not None
    assert operator.bl_label == expected


@pytest.mark.parametrize("desc", ["Description", None])
def test_builder_set_operator_doc(desc: str | None) -> None:
    model = Model()
    model.add_action(Action(id="test", desc=desc))

    builder = BlenderMenuBuilder(model, root_menu="Test Menu")
    builder.build()

    operator = builder.find_operator(model.get_action("test").id)
    assert operator is not None
    assert operator.__doc__ == desc


def test_operator_execute_cb() -> None:
    mock = Mock()
    model = Model()
    model.add_action(Action(id="test", cb=mock))

    builder = BlenderMenuBuilder(model, root_menu="Test Menu")
    builder.build()

    operator = builder.find_operator(model.get_action("test").id)
    assert operator is not None

    fn = reduce(getattr, operator.bl_idname.split("."), bpy.ops)
    assert callable(fn)
    assert fn() == {"FINISHED"}
    mock.assert_called_once()


def test_builder_set_menu_label() -> None:
    model = Model()
    model.add_menu(Menu(label="Sub Menu"))

    builder = BlenderMenuBuilder(model, root_menu="Test Menu")
    menu = builder.build()
    assert builder.find_menu(()) is menu

    sub_menu = builder.find_menu(("Sub Menu",))
    assert sub_menu is not None
    assert sub_menu.bl_label == "Sub Menu"


def test_build_demo_model() -> None:
    model = demo_model()

    builder = BlenderMenuBuilder(model, root_menu="Test Menu")
    builder.build()

    for item in model.iter(menu=(), recursive=True):
        if isinstance(item, ItemAction):
            assert builder.find_operator(item.inner.id) is not None
        elif isinstance(item, ItemMenu):
            assert builder.find_menu(item.path) is not None


def test_builder_unregister_operator() -> None:
    model = Model()
    model.add_action(Action(id="test"))

    builder = BlenderMenuBuilder(model, root_menu="Test Menu")
    builder.build()

    operator = builder.find_operator(model.get_action("test").id)
    assert operator is not None

    builder.unregister()
    operator = builder.find_operator(model.get_action("test").id)
    assert operator is None


def test_builder_unregister_before_build() -> None:
    builder = BlenderMenuBuilder(Model(), root_menu="Test Menu")
    builder.unregister()


def test_builder_unregister_twice() -> None:
    model = Model()
    model.add_action(Action(id="test"))

    builder = BlenderMenuBuilder(model, root_menu="Test Menu")
    builder.build()

    builder.unregister()
    builder.unregister()


def test_builder_find_operator_unknown_return_none() -> None:
    builder = BlenderMenuBuilder(Model(), root_menu="Test Menu")
    assert builder.find_operator("unknown") is None


def test_builder_find_menu_unknown_return_none() -> None:
    builder = BlenderMenuBuilder(Model(), root_menu="Test Menu")
    assert builder.find_menu(("unknown",)) is None
