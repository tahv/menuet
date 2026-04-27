# ruff: noqa: PLC0415
"""
/// version-added | Added in 1.3.0
///
"""  # noqa: D205, D212, D415

from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

from menuet import ItemGroup
from menuet.model import ItemAction, ItemMenu

if TYPE_CHECKING:
    from collections.abc import Callable

    import unreal

    from menuet.model import MenuSortKey, Model

__all__ = (
    "UnrealMenuBuilder",
    "model_reference_to_string_command",
)


def model_reference_to_string_command(reference: str) -> Callable[[str], str]:
    """Generate the `to_string_command` argument from a [`Model`][menuet.Model] reference.

    Args:
        reference: Points to a Callable returning a [`Model`][menuet.Model]
            in the form `importable.module:function`.

    Example:
        ```python
        >>> func = model_reference_to_string_command('menuet.demo:demo_model')
        >>> print(func('anim-bake'))
        import menuet
        from menuet.utils import load_entry_point
        model = load_entry_point('menuet.demo:demo_model')
        if not isinstance(model, menuet.Model):
            raise TypeError(f"Expected 'Model', found '{type(model)}'")
        model.get_action('anim-bake').cb()

        ```
    """  # noqa: E501

    def inner(action: str) -> str:
        return dedent(
            f"""\
            import menuet
            from menuet.utils import load_entry_point
            model = load_entry_point('{reference}')
            if not isinstance(model, menuet.Model):
                raise TypeError(f"Expected 'Model', found '{{type(model)}}'")
            model.get_action('{action}').cb()""",
        )

    return inner


class UnrealMenuBuilder:
    """Unreal Menu Builder.

    Args:
        model: Model to build.
        parent: Parent menu.
        root_name: Root menu name. Serve as the 'owner' name of all sub-menu and entries
            created by the builder and used as an identifier during build.
        root_label: Root menu display name. Default to `root_name`.
        to_string_command: Callable that accept an `Action.id`
            and return an executable string.
            The string script should execute the `Action.cb`.
            Unreal menu entry expect a
            [string command][unreal.ToolMenuEntry.set_string_command].
        sort_key: Customize the sort order of menu items.
    """

    def __init__(
        self,
        model: Model,
        *,
        parent: unreal.ToolMenu,
        root_name: str,
        root_label: str | None = None,
        to_string_command: Callable[[str], str],
        sort_key: MenuSortKey | None = None,
    ) -> None:
        self._model: Model = model
        self._sort_key = sort_key
        self._root_name: str = root_name
        self._root_label: str = root_label or root_name
        self._to_string_command = to_string_command
        self._parent: unreal.ToolMenu = parent

    def unregister(self) -> None:
        """Unregister menu, if it exist."""
        import unreal

        tool_menus = unreal.ToolMenus.get()
        tool_menus.unregister_owner_by_name(unreal.Name(self._root_name))

    def build(self) -> unreal.ToolMenu:
        """Build menu."""
        import unreal

        self.unregister()

        root = self._parent.add_sub_menu(
            owner=unreal.Name(self._root_name),
            section_name=unreal.Name(""),
            name=unreal.Name(self._root_name),
            label=unreal.Text(self._root_label),
            tool_tip=unreal.Text(""),
        )

        menus: dict[tuple[str, ...], unreal.ToolMenu] = {(): root}
        for item in self._model.iter(sort_key=self._sort_key, recursive=True):
            parent = menus[item.menu]

            if isinstance(item, ItemGroup):
                parent.add_section(
                    section_name=unreal.Name(item.inner or "Ungrouped"),
                    label=unreal.Text(item.inner or ""),
                )

            elif isinstance(item, ItemMenu):
                menu = parent.add_sub_menu(
                    owner=unreal.Name(self._root_name),
                    section_name=unreal.Name(item.inner.group or ""),
                    name=unreal.Name(item.inner.label),
                    label=unreal.Text(item.inner.label),
                    tool_tip=unreal.Text(item.inner.desc or ""),
                )
                menus[item.path] = menu

            elif isinstance(item, ItemAction):
                entry = unreal.ToolMenuEntry(
                    name=unreal.Name(item.inner.id),
                    owner=unreal.ToolMenuOwner(unreal.Name(self._root_name)),
                    type=unreal.MultiBlockType.MENU_ENTRY,
                    insert_position=unreal.ToolMenuInsert(
                        position=unreal.ToolMenuInsertType.LAST,
                    ),
                )
                entry.set_label(unreal.Text(item.inner.label or item.inner.id))
                entry.set_tool_tip(unreal.Text(item.inner.desc or ""))
                entry.set_string_command(
                    type=unreal.ToolMenuStringCommandType.PYTHON,
                    custom_type=unreal.Name(""),
                    string=self._to_string_command(item.inner.id),
                )
                parent.add_menu_entry(
                    section_name=unreal.Name(item.inner.group or ""),
                    args=entry,
                )

            else:  # pragma: no cover
                raise TypeError(item)

        unreal.ToolMenus.get().refresh_all_widgets()
        return root
