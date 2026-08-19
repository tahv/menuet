# ruff: noqa: N802 N803 PLR0917 FBT001 FBT002
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Protocol, cast

from menuet.model import ItemAction, ItemGroup, ItemMenu, Model

if TYPE_CHECKING:
    from collections.abc import Callable
    from importlib.abc import Traversable

    import nuke
    from PySide6.QtGui import QAction

    from menuet import Action
    from menuet.model import MenuSortKey, Model


__all__ = ("NukeMenuBuilder",)


class NukeMenu(Protocol):
    """Nuke menu protocol.

    Members shared by
    [nuke.Menu](https://learn.foundry.com/nuke/developers/16.0/pythondevguide/_autosummary/nuke.Menu.html),
    [nuke.MenuBar](https://learn.foundry.com/nuke/developers/16.0/pythondevguide/_autosummary/nuke.MenuBar.html)
    and [nuke.ToolBar](https://learn.foundry.com/nuke/developers/16.0/pythondevguide/_autosummary/nuke.ToolBar.html)
    """

    def addAction(self, action: QAction) -> bool:
        """Adds the [QAction][PySide6.QtGui.QAction] to the menu."""

    def addCommand(
        self,
        name: str,
        command: str | Callable[[], Any] | None = None,
        shortcut: str | None = None,
        icon: str | None = None,
        tooltip: str = "",
        index: int = -1,
        readonly: bool = False,
        shortcutContext: Literal[0, 1, 2] = 0,
        tag: Literal[0, 1, 2] = 0,
        tagTarget: Literal[0, 1, 2, 3, 7] = 0,
        nodeClass: str | None = None,
    ) -> nuke.MenuItem:
        """Add a new command to this menu/toolbar."""

    def addMenu(
        self,
        name: str,
        icon: str | None = None,
        tooltip: str | None = None,
        index: int = -1,
        tag: Literal[0, 1, 2] = 0,
    ) -> nuke.Menu:
        """Add a new submenu."""

    def addSeparator(self, index: int = -1) -> nuke.MenuItem:
        """Add a separator to this menu/toolbar."""

    def clearMenu(self, name: str) -> bool:
        """Clears a menu."""

    def findItem(self, name: str) -> nuke.Menu | nuke.MenuItem | None:
        """Finds a submenu or command with a particular name."""

    def removeItem(self, name: str) -> bool:
        """Removes a submenu or command with a particular name.

        If the containing menu becomes empty, it will be removed too.
        """


class NukeMenuBuilder:
    """Nuke Menu Builder.

    Args:
        model: Model to build.
        root_menu: Root menu name.
        parent: Specify the `nuke.Menu`, `nuke.MenuBar` or `nuke.ToolBar`
            the menu will appear in.
        sort_key: Customize the sort order of menu items.
        get_shortcut: Callable that accept an [Action][menuet.Action]
            and return a Nuke shortcut, such as `'R'`, `'F5'` or `'Ctrl-H'`.
            If the callable returns `None`, no shortcut is assigned to the action.
            Note that this overrides pre-existing other uses for the shortcut.

    /// version-added | Added in 1.8.0
    ///
    """

    def __init__(
        self,
        model: Model,
        *,
        root_menu: str,
        # TODO(tga): root_index: int = -1
        parent: nuke.Menu | nuke.MenuBar | nuke.MenuItem,
        sort_key: MenuSortKey | None = None,
        get_shortcut: Callable[[Action], str | None] | None = None,
    ) -> None:
        self._model: Model = model
        self._sort_key = sort_key
        self._parent = cast("NukeMenu", parent)
        self._root_menu = root_menu
        self._get_shortcut = get_shortcut or (lambda _: None)

    def delete(self) -> None:
        """Delete menu if it exist."""
        self._parent.removeItem(self._root_menu)

    def build(self) -> nuke.Menu:
        """Build menu."""
        root_menu = self._parent.addMenu(name=self._root_menu)

        menus: dict[tuple[str, ...], NukeMenu] = {(): cast("NukeMenu", root_menu)}
        for item in self._model.iter(sort_key=self._sort_key, recursive=True):
            parent = menus[item.menu]

            if isinstance(item, ItemGroup):
                parent.addSeparator()

            elif isinstance(item, ItemMenu):
                menu = parent.addMenu(
                    name=item.inner.label,
                    icon=_to_nuke_icon(item.inner.icon),
                )
                menus[item.path] = cast("NukeMenu", menu)

            elif isinstance(item, ItemAction):
                parent.addCommand(
                    name=(item.inner.label or item.inner.id),
                    command=item.inner.cb,
                    shortcut=self._get_shortcut(item.inner),
                    icon=_to_nuke_icon(item.inner.icon),
                    tooltip=item.inner.desc or "",
                )

            else:  # pragma: no cover
                raise TypeError(item)

        return root_menu


def _to_nuke_icon(icon: Traversable | None) -> str | None:
    return str(icon) if isinstance(icon, Path) else None
