from __future__ import annotations

import enum
from itertools import accumulate
from typing import TYPE_CHECKING

from attrs import frozen

from menuet.model import ItemAction, ItemGroup, ItemMenu

if TYPE_CHECKING:
    from menuet.model import MenuSortKey, Model


__all__ = ("Render", "TextMenuBuilder")


@frozen
class _Render:
    child: str
    last_child: str
    menu: str
    empty: str
    group_suffix: str


class Render(enum.Enum):
    """[`TextMenuBuilder`][menuet.builders.text.TextMenuBuilder] render options."""

    UTF8 = _Render(
        child="├── ",
        last_child="└── ",
        menu="│   ",
        empty="    ",
        group_suffix=" ───",
    )
    ASCII = _Render(
        child="|-- ",
        last_child="`-- ",
        menu="|   ",
        empty="    ",
        group_suffix=" ---",
    )


def _get_item_label(item: ItemMenu | ItemAction | ItemGroup) -> str:
    if isinstance(item, ItemMenu):
        return item.inner.label
    if isinstance(item, ItemAction):
        return item.inner.label or item.inner.id
    if isinstance(item, ItemGroup):
        return item.inner or ""
    raise TypeError(type(item))  # pragma: no cover


class TextMenuBuilder:
    """Text menu builder."""

    def __init__(
        self,
        model: Model,
        *,
        root_menu: str | None = None,
        sort_key: MenuSortKey | None = None,
        render: Render = Render.ASCII,
    ) -> None:
        self._model: Model = model
        self._render: _Render = render.value
        self._sort_key: MenuSortKey | None = sort_key
        self._root_menu: str | None = root_menu

    def build(self) -> str:
        """Build menu."""
        items = list(self._model.iter(sort_key=self._sort_key, recursive=True))
        root = (self._root_menu,) if self._root_menu is not None else ()

        # mapping of `{menu_path: item_path}` of last element for each `menu_path`
        lasts: dict[tuple[str, ...], tuple[str, ...]] = {}
        for item in items:
            path = (*root, *item.path)
            lasts[path[:-1]] = path

        lasts_ = set(lasts.values())
        lines: list[str] = []

        if self._root_menu is not None:
            line = self._get_ascii_line(label=self._root_menu, path=(), lasts=lasts_)
            lines.append(line)

        for item in items:
            line = self._get_ascii_line(
                label=_get_item_label(item),
                path=(*root, *item.path),
                lasts=lasts_,
            )
            if isinstance(item, ItemGroup):
                line = f"{line}{self._render.group_suffix}"
            lines.append(line)

        return "\n".join(lines)

    def _get_ascii_line(
        self,
        label: str,
        *,
        path: tuple[str, ...] = (),
        lasts: set[tuple[str, ...]],
    ) -> str:
        chunks: list[str] = []

        parents = path[:-1]
        if parents:
            # ("a", "b", "c") -> ("a", "b") ("a", "b", "c")
            it: accumulate[tuple[str, ...]] = accumulate(
                parents,
                lambda t, s: (*t, s),
                initial=(),
            )
            next(it)  # skip initial
            next(it)  # skip root
            for menu in it:
                chunk = self._render.empty if menu in lasts else self._render.menu
                chunks.append(chunk)
            chunk = self._render.last_child if path in lasts else self._render.child
            chunks.append(chunk)

        chunks.append(label)
        return "".join(chunks)
