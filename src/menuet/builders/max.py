# ruff: noqa: A002 N803 N815
"""
/// version-added | Added in 1.4.0
///
"""  # noqa: D205, D212, D415

from __future__ import annotations

import itertools
import string
import uuid
from functools import partial
from textwrap import dedent
from typing import Protocol

from menuet import Action, ItemAction, ItemGroup, ItemMenu, MenuSortKey, Model

__all__ = ("MaxDynamicMenuBuilder",)


class MaxDynamicMenuBuilder:
    """3ds Max Dynamic Menu Builder for the Main Menu Bar.

    Menu is added before the 'Help' menu.

    Derived from 3ds Max
    [Working With Menus](https://help.autodesk.com/view/MAXDEV/2027/ENU/?guid=MAXDEV_Python_using_pymxs_pymxs_macroscripts_menus_html)
    documentation.

    Args:
        model: Model to build.
        root_menu: Root menu name.
        sort_key: Customize the sort order of menu items.
    """

    def __init__(
        self,
        model: Model,
        *,
        root_menu: str,
        sort_key: MenuSortKey | None = None,
    ) -> None:
        self._model: Model = model
        self._sort_key = sort_key
        self._root_menu = root_menu
        self._builder_uid = _hex_to_ascii_lowercase(uuid.uuid4().hex)

    def build(self) -> None:
        """Build menu."""
        import pymxs

        actions: dict[int, Action] = {}
        # inject handlers in the global maxscript namespace so we can call them from mxs

        # the first handler takes a 'root menu' and populate it with actions
        populate_attr = f"menuet_populate_{self._builder_uid}"
        setattr(
            pymxs.runtime,
            populate_attr,
            partial(_populate_dynamic_menu, self._model, self._sort_key, actions),
        )

        # the second handler takes an action id and execute it.
        exec_attr = f"menuet_exec_{self._builder_uid}"
        setattr(
            pymxs.runtime,
            exec_attr,
            partial(_execute_dynamic_menu_action, actions),
        )

        # register a macroscript creating the dynamic menu
        script_name = f"menuet{self._builder_uid}"
        category = "Menuet"
        label = self._root_menu
        pymxs.runtime.execute(
            dedent(f"""\
            macroscript {script_name}
            category:"{category}"
            buttonText:"{label}"
            (
              on populateDynamicMenu menuRoot do {populate_attr} menuRoot
              on dynamicMenuItemSelected id do {exec_attr} id
            )
            """),
        )

        # The optional 'id' parameter lets us tag one or a group of callbacks
        # with a unique name so that we can remove them all as a group
        # without interfering with other callbacks.
        callback_id = pymxs.runtime.name(f"MenuetDynamicMenu{self._builder_uid}")
        pymxs.runtime.callbacks.removescripts(id=callback_id)
        pymxs.runtime.callbacks.addscript(
            pymxs.runtime.name("cuiRegisterMenus"),
            partial(_register_menu, label, f"{script_name}`{category}"),
            id=callback_id,
        )


def _register_menu(menu_name: str, action_identifier: str) -> None:
    """Register the menu and its items Max main menu bar."""
    import pymxs

    menu_man = pymxs.runtime.callbacks.notificationparam()
    menu_bar = menu_man.mainmenubar
    menu: _StandardMenu = menu_bar.createsubmenu(
        pymxs.runtime.genGUID(),
        menu_name,
        beforeid="cee8f758-2199-411b-81e7-d3ff4a80d143",  # help menu id
    )
    action = menu.createaction(
        pymxs.runtime.genGUID(),
        647394,  # 3ds Max System MacroScripts Action Table ID
        action_identifier,  # "name`category`"
    )
    action.isFlat = True


def _execute_dynamic_menu_action(actions: dict[int, Action], uid: int) -> None:
    actions[uid].cb()


def _populate_dynamic_menu(
    model: Model,
    sort_key: MenuSortKey | None,
    actions: dict[int, Action],
    root: _DynamicMenu,
) -> None:
    id_iterator = itertools.count(start=max((999, *actions.keys())) + 1)
    menus: dict[tuple[str, ...], _DynamicMenu] = {(): root}

    for item in model.iter(sort_key=sort_key, recursive=True):
        parent = menus[item.menu]

        if isinstance(item, ItemGroup):
            parent.addseparator()

        elif isinstance(item, ItemMenu):
            menu = parent.addsubmenu(item.inner.label)
            menus[item.path] = menu

        elif isinstance(item, ItemAction):
            item_id = next(id_iterator)
            parent.additem(item_id, item.inner.label or item.inner.id)
            actions[item_id] = item.inner


def _hex_to_ascii_lowercase(s: str) -> str:
    """Convert a `[a-fA-F0-9]+` string to `[a-v]+`.

    Example:
        >>> _hex_to_ascii_lowercase("abcdefABCDEF0123456789")
        'abcdefghijklmnopqrstuv'
    """
    result = ""
    for c in s:
        if c in "abcdef":
            result += c
        elif c in "ABCDEF":
            result += string.ascii_lowercase[ord(c) - 59]
        elif c in string.digits:
            result += string.ascii_lowercase[ord(c) - 36]
        else:
            raise ValueError(c)
    return result


class _DynamicMenu(Protocol):
    def additem(
        self,
        id: int,
        label: str,
        *,
        iconName: str | None = None,
        toolTip: str | None = None,
    ) -> None: ...
    def addseparator(self) -> None: ...
    def addsubmenu(self, label: str) -> _DynamicMenu: ...


class _StandardMenu(Protocol):
    def createaction(
        self,
        guid: str,
        macroscriopt_tableid: int,
        action_identifier: str,
        /,
    ) -> _StandardAction: ...


class _StandardAction(Protocol):
    isFlat: bool
