from __future__ import annotations

from typing import TYPE_CHECKING

import unreal

from menuet.builders.unreal import UnrealMenuBuilder
from menuet.demo import demo_model

if TYPE_CHECKING:
    from collections.abc import Callable


def to_string_command_factory(model: str) -> Callable[[str], str]:
    """Generate `to_string_command` argument from a `Model` reference."""

    def inner(action: str) -> str:
        return f"""\
        from importlib.metadata import EntryPoint
        model_loader = EntryPoint(name="", group="", value='{model}').load()
        model = model_loader()
        model.get_action('{action}').cb()
        """

    return inner


tool_menus = unreal.ToolMenus.get()
model = demo_model()
builder = UnrealMenuBuilder(
    model,
    root_name="Demo",
    to_string_command=to_string_command_factory("menuet.demo:demo_model"),
    parent=tool_menus.find_menu(unreal.Name("LevelEditor.MainMenu")),
)
builder.build()
