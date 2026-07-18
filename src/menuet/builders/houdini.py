"""
/// version-added | Added in 1.5.0
///
"""  # noqa: D205, D212, D415

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, NamedTuple, TypeAlias
from xml.dom.minidom import parseString
from xml.etree import ElementTree as ET

from menuet.model import ItemAction, ItemGroup, ItemMenu

if TYPE_CHECKING:
    from collections.abc import Callable

    from menuet.model import MenuSortKey, Model


__all__ = (
    "HoudiniXmlMainMenuBuilder",
    "InsertAfter",
    "InsertAtIndex",
    "InsertBefore",
    "InsertPosition",
)


class InsertBefore(NamedTuple):
    """Insert item before specified `id` item, or at the beginning of the menu."""

    id: str | None = None


class InsertAfter(NamedTuple):
    """Insert item after specified `id` item, or at the end of the menu."""

    id: str | None = None


class InsertAtIndex(NamedTuple):
    """Insert item at the `n` position in the menu."""

    n: int


InsertPosition: TypeAlias = InsertBefore | InsertAfter | InsertAtIndex
"""Fine-tune the position of script item within its menu."""


# TODO(tga): Context menu files
# TODO(tga): VOP FX menu file


class HoudiniXmlMainMenuBuilder:
    """Houdini XML Menu Builder.

    Generate a XML configuration following the Houdini
    [main menu file](https://www.sidefx.com/docs/houdini/basics/config_menus.html#main-menu-files)
    format.

    Args:
        model: Model to build.
        root_menu: Root menu name.
        to_string_command: Callable that accept an `Action.id`
            and return an executable string.
            The string script should execute the `Action.cb`.
            Houdini [menu items](https://www.sidefx.com/docs/houdini/basics/config_menus.html#menu-items)
            expect a `<scriptCode>` tag containing a Python script.
        sort_key: Customize the sort order of menu items.
        position: Insert menu at position.
    """

    def __init__(
        self,
        model: Model,
        *,
        root_menu: str,
        to_string_command: Callable[[str], str],
        sort_key: MenuSortKey | None = None,
        position: InsertPosition | None = None,
    ) -> None:
        self._model = model
        self._root_menu = root_menu
        self._to_string_command = to_string_command
        self._sort_key = sort_key
        self._position = position

    def build(self) -> str:
        """Return a XML menu configuration string."""
        main_menu = ET.Element("mainMenu")
        menu_bar = ET.SubElement(main_menu, "menuBar")
        root = _insert_sub_menu(self._root_menu, menu_bar, position=self._position)
        menus: dict[tuple[str, ...], ET.Element] = {(): root}

        for item in self._model.iter(sort_key=self._sort_key, recursive=True):
            parent = menus[item.menu]

            if isinstance(item, ItemGroup):
                if item.inner is None:  # pragma: no cover
                    ET.SubElement(parent, "separatorItem")
                else:
                    title = ET.SubElement(parent, "titleItem")
                    label = ET.SubElement(title, "label")
                    label.text = item.inner

            elif isinstance(item, ItemMenu):
                submenu = _insert_sub_menu(item.inner.label, parent)
                menus[item.path] = submenu

            elif isinstance(item, ItemAction):
                script_item = ET.SubElement(parent, "scriptItem")
                # TODO(tga): expose to_houdini_id callback
                script_item.attrib["id"] = item.inner.id
                script_code = ET.SubElement(script_item, "scriptCode")
                code = self._to_string_command(item.inner.id)
                script_code.text = f"<![CDATA[\n{code.strip()}]]>"
                label = ET.SubElement(script_item, "label")
                label.text = item.inner.label or item.inner.id

            else:  # pragma: no cover
                raise TypeError(item)

        string = ET.tostring(main_menu)
        string = string.replace(b"&lt;![CDATA[", b"<![CDATA[")
        string = string.replace(b"]]&gt;", b"]]>")

        return (
            parseString(string)  # noqa: S318
            .toprettyxml(indent="  ", encoding="utf-8")
            .decode("utf-8")
            .strip()
        )


def _insert_sub_menu(
    label: str,
    parent: ET.Element,
    *,
    position: InsertPosition | None = None,
) -> ET.Element:
    menu = ET.SubElement(parent, "subMenu")
    # TODO(tga): menu.attrib["id"] = uuid.uuid4().hex
    label_item = ET.SubElement(menu, "label")
    label_item.text = label

    if position is None:
        pass
    elif isinstance(position, InsertBefore):
        insert = ET.SubElement(menu, "insertBefore")
        insert.text = position.id
    elif isinstance(position, InsertAfter):
        insert = ET.SubElement(menu, "insertAfter")
        insert.text = position.id
    elif isinstance(position, InsertAtIndex):
        insert = ET.SubElement(menu, "insertAtIndex")
        insert.text = str(position.n)
    else:  # pragma: no cover
        raise TypeError(type(insert))

    return menu
