# ruff: noqa: ARG001 ARG005
"""
/// version-added | Added in 1.1.0
///
"""  # noqa: D205, D212, D415

from __future__ import annotations

import itertools
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, TypeAlias, cast

import bpy
import bpy.utils.previews

from menuet import Action, Menu
from menuet.model import ItemAction, ItemGroup, ItemMenu

if TYPE_CHECKING:
    from collections.abc import Callable

    from bpy.stub_internal.rna_enums import OperatorReturnItems
    from bpy.utils.previews import ImagePreviewCollection

    from menuet.model import MenuSortKey, Model

    MenuDraw: TypeAlias = Callable[[bpy.types.Menu, bpy.types.Context], None]

__all__ = ("BlenderMenuBuilder",)


class BlenderMenuBuilder:
    """Blender Menu Builder.

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
        self._preview_collection: ImagePreviewCollection | None = None
        self._registered_menus: dict[tuple[str, ...], type[bpy.types.Menu]] = {}
        self._registered_operators: dict[str, type[bpy.types.Operator]] = {}

    def find_operator(self, id: str) -> type[bpy.types.Operator] | None:  # noqa: A002
        """Find Blender operator created by the `build` method."""
        return self._registered_operators.get(id)

    def find_menu(self, path: tuple[str, ...]) -> type[bpy.types.Menu] | None:
        """Find Blender menu created by the `build` method."""
        return self._registered_menus.get(path)

    def unregister(self) -> None:
        """Unregister all operators and menus registered by the last `build` call."""
        for class_ in itertools.chain[type[bpy.types.Operator | bpy.types.Menu]](
            self._registered_operators.values(),
            self._registered_menus.values(),
        ):
            bpy.utils.unregister_class(class_)
        self._registered_operators.clear()
        self._registered_menus.clear()
        if self._preview_collection is not None:
            self._preview_collection.clear()
            bpy.utils.previews.remove(self._preview_collection)
            self._preview_collection = None

    def build(self) -> type[bpy.types.Menu]:
        """Build menu."""
        self.unregister()
        self._preview_collection = bpy.utils.previews.new()

        root, _ = _menu_factory(Menu(label=self._root_menu), self._preview_collection)
        bpy.utils.register_class(root)
        self._registered_menus[()] = root

        for item in self._model.iter(sort_key=self._sort_key, recursive=True):
            parent = self._registered_menus[item.menu]

            if isinstance(item, ItemGroup):
                parent.append(lambda self, context: self.layout.separator())

            elif isinstance(item, ItemMenu):
                menu, draw_func = _menu_factory(item.inner, self._preview_collection)
                bpy.utils.register_class(menu)
                self._registered_menus[item.path] = menu
                parent.append(draw_func)

            elif isinstance(item, ItemAction):
                op, draw_func = _operator_factory(item.inner, self._preview_collection)
                bpy.utils.register_class(op)
                self._registered_operators[item.inner.id] = op
                parent.append(draw_func)

            else:  # pragma: no cover
                raise TypeError(item)

        return root


def _menu_factory(
    menu: Menu,
    preview_collection: ImagePreviewCollection,
) -> tuple[type[bpy.types.Menu], MenuDraw]:
    uid = str(uuid.uuid4()).replace("-", "")
    idname = f"MENUET_MT_{uid}"

    def menu_draw(
        self: bpy.types.Menu,
        context: bpy.types.Context,
    ) -> None:  # pragma: no cover
        assert self.layout is not None

        image_preview = preview_collection.get(idname)
        if image_preview is None and isinstance(menu.icon, Path):
            image_preview = preview_collection.load(idname, str(menu.icon), "IMAGE")
        icon_value = image_preview.icon_id if image_preview is not None else 0

        self.layout.menu(idname, icon_value=icon_value)

    def draw(
        self: bpy.types.Menu,
        context: bpy.types.Context,
    ) -> None:  # pragma: no cover
        pass

    cls = cast(
        "type[bpy.types.Menu]",
        type(
            f"MenuetMenu_{uid}",
            (bpy.types.Menu,),
            {
                "bl_idname": idname,
                "bl_label": menu.label,
                "draw": draw,
            },
        ),
    )

    return (cls, menu_draw)


def _operator_factory(
    action: Action,
    preview_collection: ImagePreviewCollection,
) -> tuple[type[bpy.types.Operator], MenuDraw]:
    uid = str(uuid.uuid4()).replace("-", "")
    idname = f"menuet.{uid}"

    def menu_draw(
        self: bpy.types.Menu,
        context: bpy.types.Context,
    ) -> None:  # pragma: no cover
        assert self.layout is not None

        image_preview = preview_collection.get(idname)
        if image_preview is None and isinstance(action.icon, Path):
            image_preview = preview_collection.load(idname, str(action.icon), "IMAGE")
        icon_value = image_preview.icon_id if image_preview is not None else 0

        self.layout.operator(idname, icon_value=icon_value)

    def execute(self: bpy.types.Operator, context: object) -> set[OperatorReturnItems]:
        """Execute operator."""
        action.cb()
        return {"FINISHED"}

    cls = cast(
        "type[bpy.types.Operator]",
        type(
            f"MenuetOperator_{uid}",
            (bpy.types.Operator,),
            {
                "bl_idname": idname,
                "bl_label": action.label or action.id,
                "__doc__": action.desc,
                "execute": execute,
            },
        ),
    )

    return (cls, menu_draw)
