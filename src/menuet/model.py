from __future__ import annotations

import sys
from collections.abc import Callable
from functools import reduce
from itertools import chain
from operator import getitem
from typing import TYPE_CHECKING, Any, NamedTuple

import attr
from attrs import define, field

from menuet.action import Action
from menuet.menu import Menu

if sys.version_info < (3, 11):
    import tomli as tomllib  # ty: ignore[unresolved-import]
else:
    import tomllib

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from _typeshed import SupportsRead, SupportsRichComparison


__all__ = (
    "ItemAction",
    "ItemGroup",
    "ItemMenu",
    "MenuSortKey",
    "Model",
    "deserialize",
    "load",
    "loads",
)


@define
class _MenuNode:
    inner: Menu
    parent: _MenuNode | None
    menus: dict[str, _MenuNode] = field(factory=dict, init=False)
    actions: dict[str, _ActionNode] = field(factory=dict, init=False)


@define
class _ActionNode:
    inner: Action = field(on_setattr=attr.setters.frozen)
    parent: _MenuNode


def load(
    fp: SupportsRead[bytes],
    model: Model,
    root_keys: tuple[str, ...] | None = None,
) -> None:
    """Load `fp` and deserialize its content to [`model`][menuet.Model].

    Args:
        fp: a `.read()`-supporting file-like object containing a TOML document.
        model: Target model.
        root_keys: The sequence of keys that lead to the root configuration structure.
            For example, a `[tool.myapp.mymenu]` table (`("tool", "myapp", "mymenu")`)
            in `pyproject.toml`.
    """
    config = tomllib.load(fp)
    deserialize(config, model, root_keys)


def loads(s: str, model: Model, root_keys: tuple[str, ...] | None = None) -> None:
    """Load `s` and deserialize its content to [`model`][menuet.Model].

    Args:
        s: a `str` containing a TOML document.
        model: Target model.
        root_keys: The sequence of keys that lead to the root configuration structure.
            For example, a `[tool.myapp.mymenu]` table (`("tool", "myapp", "mymenu")`)
            in `pyproject.toml`.
    """
    config = tomllib.loads(s)
    deserialize(config, model, root_keys)


def deserialize(
    config: dict[str, Any],
    model: Model,
    root_keys: tuple[str, ...] | None = None,
) -> None:
    """Deserialize `config` and add its content to the model.

    Args:
        config: A dict containing a configuration of menus and actions.
        model: Target model.
        root_keys: The sequence of keys that lead to the root configuration structure.
            For example, a `[tool.myapp.mymenu]` table (`("tool", "myapp", "mymenu")`)
            in `pyproject.toml`.
    """
    root_keys = root_keys if root_keys is not None else ()
    # TODO(tga): try/except KeyError
    config = reduce(getitem, root_keys, config)
    for c in config.get("menu", []):
        model.add_menu(Menu.deserialize(c))
    for c in config.get("action", []):
        model.add_action(Action.deserialize(c))


class ItemGroup(NamedTuple):
    """Group wrapper, returned by [`Model.iter`][menuet.Model.iter]."""

    inner: str | None
    menu: tuple[str, ...]

    @property
    def path(self) -> tuple[str, ...]:  # noqa: D102
        return (*self.menu, self.inner or "")


class ItemMenu(NamedTuple):
    """Menu wrapper, returned by [`Model.iter`][menuet.Model.iter]."""

    inner: Menu

    @property
    def menu(self) -> tuple[str, ...]:  # noqa: D102
        return self.inner.menu

    @property
    def path(self) -> tuple[str, ...]:  # noqa: D102
        return (*self.inner.menu, self.inner.label)


class ItemAction(NamedTuple):
    """Action wrapper, returned by [`Model.iter`][menuet.Model.iter]."""

    inner: Action

    @property
    def menu(self) -> tuple[str, ...]:  # noqa: D102
        return self.inner.menu

    @property
    def path(self) -> tuple[str, ...]:  # noqa: D102
        return (*self.inner.menu, self.inner.id)


MenuSortKey = Callable[[Menu | Action], "SupportsRichComparison"]
"""[Mode.iter][menuet.Model.iter] sort [key function](https://docs.python.org/3/howto/sorting.html#key-functions).

Must be a function that accepts a Menu or Action argument
that is used to extract a comparison key from each element.
"""


def _default_sort_key(node: Menu | Action) -> SupportsRichComparison:
    """Default sort key for `Menu` items."""
    label = (node.label or node.id) if isinstance(node, Action) else node.label
    return (
        (node.group or "").lower(),
        not isinstance(node, Menu),
        label.lower(),
    )


class Model:
    """The main `Action` and `Menu` storage abstraction."""

    def __init__(self) -> None:
        self._actions: dict[str, Action] = {}
        self._menus: dict[tuple[str, ...], _MenuNode] = {}
        self._menus[()] = _MenuNode(Menu(label="", menu=()), parent=None)

    def add_action(self, action: Action) -> None:
        """Add `action` to model."""
        self._add_action(action)

    def add_menu(self, menu: Menu) -> None:
        """Add `menu` to model."""
        self._add_menu(menu)

    def get_action(self, id: str) -> Action:  # noqa: A002
        """Return `Action` with given `id` in model.

        Raises:
            KeyError: `id` not found.
        """
        return self._actions[id]

    def iter(
        self,
        menu: tuple[str, ...] = (),
        *,
        sort_key: MenuSortKey | None = None,
        recursive: bool = False,
    ) -> Iterator[ItemGroup | ItemMenu | ItemAction]:
        """Iter menu items.

        By default, menu items are sorted as follow:

        1. Sort groups, alphabetically
        2. In the current group, place menus above actions
        3. Sort elements alphabetically

        Args:
            menu: The start menu. An empty tuple `()` (the default), starts at the top.
            sort_key: Customize the sort order of menu items.
            recursive: Iter sub-menus in depth-first search.
        """
        sort_key = sort_key or _default_sort_key
        parent = self._menus[menu]
        for item in self._iter_menu(parent, sort_key):
            yield item
            if isinstance(item, ItemMenu) and recursive:
                yield from self.iter(
                    menu=(*item.inner.menu, item.inner.label),
                    sort_key=sort_key,
                    recursive=True,
                )

    def _iter_menu(
        self,
        menu: _MenuNode,
        sort_key: MenuSortKey,
    ) -> Iterator[ItemGroup | ItemMenu | ItemAction]:
        previous_group = None

        nodes: Iterable[Menu | Action] = chain(
            (node.inner for node in menu.menus.values()),
            (node.inner for node in menu.actions.values()),
        )
        nodes = sorted(nodes, key=sort_key)

        for node in nodes:
            group = node.group
            if group is not None and group != previous_group:
                yield ItemGroup(group, menu=node.menu)
                previous_group = group

            yield ItemMenu(node) if isinstance(node, Menu) else ItemAction(node)

    def _add_action(self, action: Action) -> _ActionNode:
        if action.id in self._actions:
            msg = f"Action {action.id!r} already exists in model"
            raise ValueError(msg)

        # add to tree
        if action.menu:
            parent = self._menus.get(action.menu)
            if not parent:
                parent = self._add_menu(
                    Menu(label=action.menu[-1], menu=action.menu[:-1]),
                )
        else:
            parent = self._menus[()]
        node = _ActionNode(action, parent=parent)
        parent.actions[action.id] = node

        # add to map
        self._actions[action.id] = action

        return node

    def _add_menu(self, menu: Menu) -> _MenuNode:
        path = (*menu.menu, menu.label)
        if path in self._menus:
            msg = f"Menu {path!r} already exists in model"
            raise ValueError(msg)

        # add parent to tree
        parent = self._menus.get(menu.menu)
        if parent is None:
            if menu.menu:
                parent = self._add_menu(Menu(label=menu.menu[-1], menu=menu.menu[:-1]))
            else:
                parent = self._menus[()]

        # add leaf to tree
        node = parent.menus.get(menu.label)
        if node is None:
            node = _MenuNode(menu, parent=parent)
            parent.menus[menu.label] = node
        elif menu.is_configured() and not node.inner.is_configured():
            node.inner = menu

        # add to map
        self._menus[path] = node

        return node
