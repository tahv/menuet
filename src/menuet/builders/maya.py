from __future__ import annotations

import enum
import itertools
import string
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeAlias

from menuet.model import ItemAction, ItemGroup, ItemMenu, Model
from menuet.utils import complete

if TYPE_CHECKING:
    import sys
    from collections.abc import Callable

    from menuet.action import Action
    from menuet.menu import Menu
    from menuet.model import MenuSortKey, Model

    if sys.version_info < (3, 11):
        from importlib.abc import Traversable
    else:
        from importlib.resources.abc import Traversable


__all__ = (
    "MayaMarkingMenuBuilder",
    "MayaMarkingMenuModifier",
    "MayaMarkingMenuMouseButton",
    "MayaMenuBuilder",
    "RadialPosition",
)


class MayaMenuBuilder:
    """Maya Menu Builder.

    Args:
        model: Model to build.
        root_menu: Root menu name.
        parent: Specify the window or menu that the menu will appear in.
            Default to Maya main menubar.
        sort_key: Customize the sort order of menu items.
        to_drag_menu_command: Callable that accept an `Action.id`
            and return an executable string.
            The string script will be executed when the shelf button
            is **clicked** and should call the `Action.cb`.
        to_drag_double_click_command: Callable that accept an `Action.id`
            and return an executable string.
            The string script will be executed when the shelf button
            is **double clicked** and should call the `Action.cb`.

    /// version-added | Added in 1.2.0
    ///

    /// version-changed | Changed in 1.9.0

    Added `to_drag_menu_command` and `to_drag_double_click_command` arguments.

    ///
    """

    def __init__(
        self,
        model: Model,
        *,
        root_menu: str,
        parent: str = "MayaWindow",
        sort_key: MenuSortKey | None = None,
        to_drag_menu_command: Callable[[str], str] | None = None,
        to_drag_double_click_command: Callable[[str], str] | None = None,
    ) -> None:
        self._model: Model = model
        self._sort_key = sort_key
        self._parent = parent
        self._root_menu = root_menu
        self._root_long_name = f"{self._parent}|{self._root_menu}"
        self._to_drag_menu_command = to_drag_menu_command or _default_drag_menu_command
        self._to_drag_double_click_command = (
            to_drag_double_click_command or _default_drag_menu_command
        )

    def delete(self) -> None:
        """Delete menu if it exist."""
        from maya import cmds  # noqa: PLC0415

        if _is_menu(self._parent):
            cmds.deleteUI(self._root_long_name, menuItem=True)
        else:
            try:
                cmds.deleteUI(self._root_long_name, menu=True)
            except RuntimeError as exc:
                if str(exc).endswith(f"Object '{self._root_long_name}' not found."):
                    return
                raise

    def build(self) -> None:
        """Build menu."""
        from maya import cmds  # noqa: PLC0415

        if cmds.menu(self._root_long_name, exists=True):
            cmds.menu(self._root_long_name, edit=True, deleteAllItems=True)
        elif _is_menu(self._parent):
            cmds.menuItem(
                self._root_menu,
                subMenu=True,
                tearOff=True,
                label=self._root_menu,
                parent=self._parent,
            )
        else:
            # TODO(tga): RuntimeError: Layout must be a menuBarLayout: <parent>
            cmds.menu(
                self._root_menu,
                tearOff=True,
                label=self._root_menu,
                parent=self._parent,
            )

        menus: dict[tuple[str, ...], str] = {(): self._root_long_name}
        for item in self._model.iter(sort_key=self._sort_key, recursive=True):
            parent = menus[item.menu]

            if isinstance(item, ItemGroup):
                name = _unique_menu_name(item.inner or "divider")
                cmds.menuItem(
                    name,
                    divider=True,
                    dividerLabel=item.inner or "",
                    parent=parent,
                )

            elif isinstance(item, ItemMenu):
                name = _unique_menu_name(item.inner.label)
                long_name: str = cmds.menuItem(
                    name,
                    subMenu=True,
                    tearOff=True,
                    label=item.inner.label,
                    parent=parent,
                    image=_to_maya_image(item.inner.icon),
                )
                menus[item.path] = long_name

            elif isinstance(item, ItemAction):
                name = _unique_menu_name(item.inner.label or item.inner.id)
                cmds.menuItem(
                    name,
                    label=item.inner.label or item.inner.id,
                    command=item.inner.cb,
                    annotation=item.inner.desc or "",
                    image=_to_maya_image(item.inner.icon),
                    parent=parent,
                    # The dragMenuCommand will be executed immediately
                    # and that command is expected to return a string containing
                    # the actual command that will be put on the shelf button.
                    dragMenuCommand=partial(self._to_drag_menu_command, item.inner.id),
                    # The dragDoubleClickCommand works differently,
                    # it's the string that will be put on the shelf button,
                    # no intermediate callback.
                    dragDoubleClickCommand=self._to_drag_double_click_command(
                        item.inner.id
                    ),
                )

            else:  # pragma: no cover
                raise TypeError(item)


RadialPosition: TypeAlias = Literal["N", "NW", "W", "SW", "S", "SE", "E", "NE"]
"""The radial position of the menu item in a Maya Marking Menu.

Radial positions are given in the form of a cardinal direction.
"""


class MayaMarkingMenuMouseButton(enum.IntEnum):
    """The mouse button used to trigger the marking menu."""

    LEFT = 1
    """Left mouse button."""
    RIGHT = 2
    """Right mouse button."""
    MIDDLE = 3
    """Middle mouse button."""


class MayaMarkingMenuModifier(enum.Flag):
    """The modifier keys required to trigger the marking menu."""

    NONE = 0
    """No button."""
    CTRL = 1
    """The `Ctrl` button."""
    ALT = 2
    """The `Alt` button."""
    SHIFT = 4
    """The `Shift` button."""


class MayaMarkingMenuBuilder:
    """Maya Marking Menu Builder.

    Args:
        model: Model to build.
        name: Menu identifier name.
        button: Which mouse button must be pressed to trigger the marking menu.
        parent: Specify the control that the marking menu will appear in.
            Default to all Maya view panels.
        sort_key: Customize the sort order of menu items.
        modifier: Which set of modifiers must be presset to trigger the marking menu.
            Default to no required modifier keys.
        get_rp: Callable that accept an [Action][menuet.Action] or [Menu][menu.Menu]
            and return its radial position.
            If the callable returns `None`, the item is put in the menu list
            below the radial items.

    /// version-added | Added in 1.7.0
    ///
    """

    def __init__(
        self,
        model: Model,
        *,
        name: str,
        button: MayaMarkingMenuMouseButton,
        parent: str = "viewPanes",
        sort_key: MenuSortKey | None = None,
        modifier: MayaMarkingMenuModifier = MayaMarkingMenuModifier.NONE,
        get_rp: Callable[[Action | Menu], RadialPosition | None] | None = None,
    ) -> None:
        self._model: Model = model
        self._sort_key = sort_key
        self._name: str = name
        self._button = button
        self._modifier = modifier
        self._parent = parent
        self._get_rp = get_rp or (lambda _: None)

    def delete(self) -> None:
        """Delete menu if it exist."""
        from maya import cmds  # noqa: PLC0415

        try:
            cmds.deleteUI(self._name, menu=True)
        except RuntimeError as exc:
            if str(exc).endswith(f"Object '{self._name}' not found."):
                return
            raise

    def build(self) -> None:
        """Build menu."""
        from maya import cmds  # noqa: PLC0415

        cmds.popupMenu(
            self._name,
            markingMenu=True,
            parent=self._parent,
            button=int(self._button),
            altModifier=MayaMarkingMenuModifier.ALT in self._modifier,
            ctrlModifier=MayaMarkingMenuModifier.CTRL in self._modifier,
            shiftModifier=MayaMarkingMenuModifier.SHIFT in self._modifier,
            postMenuCommand=self._post_menu_command,
            postMenuCommandOnce=True,
        )

    def _post_menu_command(self, parent: str, _: str) -> None:
        from maya import cmds  # noqa: PLC0415

        menus: dict[tuple[str, ...], str] = {(): parent}
        for item in self._model.iter(sort_key=self._sort_key, recursive=True):
            parent = menus[item.menu]

            if isinstance(item, ItemGroup):
                name = _unique_menu_name(item.inner or "divider")
                cmds.menuItem(
                    name,
                    divider=True,
                    dividerLabel=item.inner or "",
                    parent=parent,
                )

            elif isinstance(item, ItemMenu):
                name = _unique_menu_name(item.inner.label)
                pos = self._get_rp(item.inner)
                long_name: str = cmds.menuItem(
                    name,
                    label=item.inner.label,
                    subMenu=True,
                    parent=parent,
                    image=_to_maya_image(item.inner.icon),
                    **({"radialPosition": pos} if pos is not None else {}),
                )  # type: ignore[call-overload]
                menus[item.path] = long_name

            elif isinstance(item, ItemAction):
                name = _unique_menu_name(item.inner.label or item.inner.id)
                pos = self._get_rp(item.inner)
                cmds.menuItem(
                    name,
                    label=item.inner.label or item.inner.id,
                    # Maya pass a bool `False` argument when calling the command
                    command=complete(item.inner.cb),
                    annotation=item.inner.desc or "",
                    parent=parent,
                    image=_to_maya_image(item.inner.icon),
                    **({"radialPosition": pos} if pos is not None else {}),
                )  # type: ignore[call-overload]

            else:  # pragma: no cover
                raise TypeError(item)


def _to_maya_image(icon: Traversable | None) -> str:
    return str(icon) if isinstance(icon, Path) else ""


def _is_menu(path: str) -> bool:
    from maya import cmds  # noqa: PLC0415

    return path in cmds.lsUI(menus=True, long=True)


def _unique_menu_name(name: str) -> str:
    """Returns a unique and legal Maya menu name."""
    from maya import cmds  # noqa: PLC0415

    name = _to_maya_name(name)

    # This set ensure a unique name across all existing menu items,
    # and is more restrictive than to Maya native check.
    existing = {
        item
        for path in cmds.lsUI(menus=True, menuItems=True, long=True)
        for item in path.split("|")
    }

    counter = itertools.count(start=1)
    current = name
    while current in existing:
        current = name + str(next(counter))

    return current


def _default_drag_menu_command(_: str) -> Callable[[], str]:
    """Returns a Callable that itself returns an empty string."""

    def inner() -> str:
        return ""

    return inner


def _to_maya_name(s: str) -> str:
    """Convert `s` into a legal Maya node name.

    Legal node names begin with any character from a-z or A-Z and an underscore,
    followed by a sequence of characters from a-z or A-Z, underscore or numerals.

    Note:
        Returned string is a **legal** name but may not be unique.

    Example:
        >>> _to_maya_name("abc")
        'abc'
        >>> _to_maya_name("Abc")
        'Abc'
        >>> _to_maya_name("_abc")
        '_abc'
        >>> _to_maya_name("abc_")
        'abc_'
        >>> _to_maya_name("1abc")
        'abc'
        >>> _to_maya_name("a-bc")
        'a_bc'
        >>> _to_maya_name("a--bc")
        'a__bc'
        >>> _to_maya_name("ab*c")
        'ab_c'
        >>> _to_maya_name("abc*")
        'abc_'
        >>> _to_maya_name("a")
        'a'
        >>> _to_maya_name("12a3")
        'a3'
        >>> _to_maya_name("123")
        Traceback (most recent call last):
            ...
        ValueError: can't convert '123' to a legal Maya node name
        >>> _to_maya_name("1")
        Traceback (most recent call last):
            ...
        ValueError: can't convert '1' to a legal Maya node name
        >>> _to_maya_name("")
        Traceback (most recent call last):
            ...
        ValueError: empty string
    """
    first = string.ascii_letters + "_"
    rest = first + string.digits
    it = iter(s)
    result = ""

    if (c := next(it, "")) and c in first:
        result += c
    elif c == "":
        msg = "empty string"
        raise ValueError(msg)
    elif c.isdigit():
        for c in it:
            if c.isdigit():
                continue
            result += c
            break
    else:
        result += "_"

    for c in it:
        result += c if c in rest else "_"

    if not result:
        msg = f"can't convert {s!r} to a legal Maya node name"
        raise ValueError(msg)

    return result
