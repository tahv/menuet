from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QAction

from menuet.model import ItemAction, ItemGroup, ItemMenu
from menuet.utils import logger

if TYPE_CHECKING:
    from importlib.resources.abc import Traversable

    from menuet.model import MenuSortKey, Model

__all__ = ("QMenuBuilder",)


class QMenuBuilder:
    """Qt Menu Builder.

    Args:
        model: Model to build.
        root_menu: Menu to populate.
            All existing actions in the menu are removed during `build`.
            If a `str` is provided, a new `QMenu` will be created.
        sort_key: Customize the sort order of menu items.
    """

    def __init__(
        self,
        model: Model,
        *,
        root_menu: QtWidgets.QMenu | str,
        sort_key: MenuSortKey | None = None,
    ) -> None:
        self._model: Model = model
        self._sort_key = sort_key
        self._root_menu = root_menu

    def build(self) -> QtWidgets.QMenu:
        """Build menu."""
        if isinstance(self._root_menu, QtWidgets.QMenu):
            root = self._root_menu
            root.clear()
        else:
            root = QtWidgets.QMenu(self._root_menu)

        menus: dict[tuple[str, ...], QtWidgets.QMenu] = {(): root}
        for item in self._model.iter(sort_key=self._sort_key, recursive=True):
            parent = menus[item.menu]

            if isinstance(item, ItemGroup):
                parent.addSection(item.inner or "")

            elif isinstance(item, ItemMenu):
                menu = QtWidgets.QMenu(item.inner.label)
                menu.setIcon(_qicon_from_file(item.inner.icon))
                menu.setToolTipsVisible(True)
                menu.setTearOffEnabled(False)
                menu.setParent(parent, menu.windowFlags())
                parent.addMenu(menu)
                menus[item.path] = menu

            elif isinstance(item, ItemAction):
                action = QAction()
                action.setText(item.inner.label or item.inner.id)
                action.setIconVisibleInMenu(True)
                action.setIcon(_qicon_from_file(item.inner.icon))
                action.setToolTip(item.inner.desc or "")
                action.triggered.connect(item.inner.cb)
                action.setParent(parent)
                parent.addAction(action)

            else:  # pragma: no cover
                raise TypeError(item)

        for menu in menus.values():
            _fix_first_separator(menu)

        return root


def _qicon_from_file(file: Traversable | None, size: int = 16) -> QtGui.QIcon:
    """Initialize `QIcon` from `file` bytes.

    If `file` is `None`, or contains an invalid pixmap,
    an empty `QIcon` is returned.
    """
    if file is None:
        return QtGui.QIcon()

    if not file.is_file():
        logger.debug("icon file does not exist or is not a file: '%s'", file)
        return QtGui.QIcon()

    pixmap = QtGui.QPixmap()
    if not pixmap.loadFromData(file.read_bytes()):
        logger.debug("failed to load icon file: '%s'", file)
        return QtGui.QIcon()

    pixmap = pixmap.scaled(
        QtCore.QSize(size, size),
        mode=QtCore.Qt.TransformationMode.SmoothTransformation,
    )
    return QtGui.QIcon(pixmap)


def _fix_first_separator(menu: QtWidgets.QMenu) -> None:
    """Fix cases where the first menu separator is not displayed.

    If the first `menu` item is a separator,
    prepend menu with a fake zero-sized action,
    making the separator the second `menu` item, and visible.
    """
    first = menu.actions()[0] if menu.actions() else None
    if first and first.isSeparator() and first.text() and first.isVisible():
        widget = QtWidgets.QWidget(menu)
        widget.setFixedSize(0, 0)
        action = QtWidgets.QWidgetAction(menu)
        action.setDefaultWidget(widget)
        menu.insertAction(first, action)
