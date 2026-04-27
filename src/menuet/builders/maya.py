"""
/// version-added | Added in 1.2.0
///
"""  # noqa: D205, D212, D415

from __future__ import annotations

import itertools
import string
from pathlib import Path
from typing import TYPE_CHECKING

from menuet import Model
from menuet.model import ItemAction, ItemGroup, ItemMenu

if TYPE_CHECKING:
    from menuet.model import MenuSortKey, Model

__all__ = ("MayaMenuBuilder",)


class MayaMenuBuilder:
    """Maya Menu Builder.

    Args:
        model: Model to build.
        root_menu: Root menu name.
        parent: Specify the window or menu that the menu will appear in.
            Default to Maya main menubar.
        sort_key: Customize the sort order of menu items.
    """

    def __init__(
        self,
        model: Model,
        *,
        root_menu: str,
        parent: str = "MayaWindow",
        sort_key: MenuSortKey | None = None,
    ) -> None:
        self._model: Model = model
        self._sort_key = sort_key
        self._parent = parent
        self._root_menu = root_menu
        self._root_long_name = f"{self._parent}|{self._root_menu}"

    def delete(self) -> None:
        """Delete menu if it exist."""
        from maya import cmds

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
        from maya import cmds

        if cmds.menu(self._root_long_name, query=True, exists=True):
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
                )
                menus[item.path] = long_name

            elif isinstance(item, ItemAction):
                name = _unique_menu_name(item.inner.label or item.inner.id)
                cmds.menuItem(
                    name,
                    label=item.inner.label or item.inner.id,
                    command=item.inner.cb,
                    # TODO(tga): dragMenuCommand: must be a str & work across sessions
                    annotation=item.inner.desc,
                    image=(
                        str(item.inner.icon)
                        if isinstance(item.inner.icon, Path)
                        else ""
                    ),
                    parent=parent,
                )

            else:  # pragma: no cover
                raise TypeError(item)


def _is_menu(path: str) -> bool:
    from maya import cmds

    return path in cmds.lsUI(menus=True, long=True)


def _unique_menu_name(name: str) -> str:
    """Returns a unique and legal Maya menu name."""
    from maya import cmds

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


def _to_maya_name(s: str) -> str:
    """Convert `s` into a legal Maya node name.

    Legal node names begin with any character from a-z or A-Z and an underscore,
    followed by a sequence of characters from a-z or A-Z, underscore or numerals.

    Note:
        Returned string is a **legal** name but may not be unique.

    Example:
        >>> to_maya_name("abc")
        'abc'
        >>> to_maya_name("Abc")
        'Abc'
        >>> to_maya_name("_abc")
        '_abc'
        >>> to_maya_name("abc_")
        'abc_'
        >>> to_maya_name("1abc")
        'abc'
        >>> to_maya_name("a-bc")
        'a_bc'
        >>> to_maya_name("a--bc")
        'a__bc'
        >>> to_maya_name("ab*c")
        'ab_c'
        >>> to_maya_name("abc*")
        'abc_'
        >>> to_maya_name("a")
        'a'
        >>> to_maya_name("12a3")
        'a3'
        >>> to_maya_name("123")
        Traceback (most recent call last):
            ...
        ValueError: can't convert '123' to a legal Maya node name
        >>> to_maya_name("1")
        Traceback (most recent call last):
            ...
        ValueError: can't convert '1' to a legal Maya node name
        >>> to_maya_name("")
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
