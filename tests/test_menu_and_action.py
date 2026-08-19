from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from menuet import Action
from menuet.menu import Menu

if TYPE_CHECKING:
    import sys

    if sys.version_info < (3, 11):
        from importlib.abc import Traversable
    else:
        from importlib.resources.abc import Traversable

# TODO(tga): test_menu_deserialize
# TODO(tga): test_action_deserialize
# TODO(tga): test_action_id_match
# TODO(tga): test_action_id_raise_value_error
# TODO(tga): test_action_cb_conversion


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        pytest.param({}, False, id="no-field"),
        pytest.param({"menu": ("Parent",)}, False, id="menu"),
        pytest.param({"group": "Test Group"}, True, id="group"),
        pytest.param({"icon": "test/icon.png"}, True, id="icon"),
        pytest.param({"desc": "Test Description"}, True, id="desc"),
        pytest.param({"extra": {"foo": "bar"}}, True, id="extra"),
    ],
)
def test_menu_is_configured(*, kwargs: dict[str, object], expected: bool) -> None:
    assert Menu(label="Test", **kwargs).is_configured() is expected  # type: ignore[arg-type]


def test_menu_extra() -> None:
    extra = {"foo": "bar", "baz": 1}
    assert Menu(label="Test", extra=extra).extra == extra


def test_action_extra() -> None:
    extra = {"foo": "bar", "baz": 1}
    assert Action(id="test", extra=extra).extra == extra


def test_menu_extra_default_to_empty_dict() -> None:
    assert Menu(label="Test").extra == {}


def test_action_extra_default_to_empty_dict() -> None:
    assert Action(id="test").extra == {}


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param(("Foo", "Bar"), ("Foo", "Bar"), id="tuple"),
        pytest.param(["Foo", "Bar"], ("Foo", "Bar"), id="list"),
        pytest.param((x for x in ("Foo", "Bar")), ("Foo", "Bar"), id="generator"),
        pytest.param({"Foo": 1, "Bar": 2}, ("Foo", "Bar"), id="dict"),
        pytest.param("Foo", ("Foo",), id="str"),
    ],
)
def test_menu_menu_conversion(*, value: object, expected: tuple[str, ...]) -> None:
    assert Menu(label="Test", menu=value).menu == expected


MENU_CONVERSION_PARAMS = [
    pytest.param(1, id="wrong-type"),
    pytest.param((1,), id="wrong-member-type"),
]


@pytest.mark.parametrize(("value"), MENU_CONVERSION_PARAMS)
def test_menu_menu_validator_raise_type_error(value: object) -> None:
    with pytest.raises(TypeError):
        Menu(label="Test", menu=value)


@pytest.mark.parametrize(("value"), MENU_CONVERSION_PARAMS)
def test_action_menu_validator_raise_type_error(value: object) -> None:
    with pytest.raises(TypeError):
        Action(id="test", menu=value)


ICON_CONVERSION_PARAMS = [
    pytest.param(None, None, id="none"),
    pytest.param("foo/bar.png", Path("foo/bar.png"), id="str"),
    pytest.param("path:foo/bar.png", Path("foo/bar.png"), id="scheme-path"),
    pytest.param(
        "res:menuet.demo:lucide-info.svg",
        Path("src/menuet/demo/lucide-info.svg").absolute(),
        id="scheme-res",
    ),
    pytest.param(
        "res:menuet.demo:unknown.svg",
        Path("src/menuet/demo/unknown.svg").absolute(),
        id="scheme-res-unknown-filename",
    ),
    pytest.param("res:foo.bar:unknown.svg", None, id="scheme-res-unknown-path"),
]


@pytest.mark.parametrize(("value", "expected"), ICON_CONVERSION_PARAMS)
def test_menu_icon_conversion(*, value: object, expected: Traversable | None) -> None:
    assert Menu(label="Test", icon=value).icon == expected


@pytest.mark.parametrize(("value", "expected"), ICON_CONVERSION_PARAMS)
def test_action_icon_conversion(*, value: object, expected: Traversable | None) -> None:
    assert Action(id="test", icon=value).icon == expected


def test_menu_icon_conversion_raise_type_error() -> None:
    with pytest.raises(TypeError):
        Menu(label="Test", icon=1)


def test_action_icon_conversion_raise_type_error() -> None:
    with pytest.raises(TypeError):
        Action(id="test", icon=1)


def test_action_cb_conversion_raise_type_error() -> None:
    with pytest.raises(TypeError):
        Action(id="test", cb=1)
