from __future__ import annotations

from functools import partial
from textwrap import dedent

import unreal

from menuet.builders.unreal import UnrealMenuBuilder
from menuet.demo import demo_model


def action_script(action: str, /, model: str) -> str:
    return dedent(f"""\
    from importlib.metadata import EntryPoint
    model_loader = EntryPoint(name="", group="", value='{model}').load()
    model = model_loader()
    model.get_action('{action}').cb()
    """)


model = demo_model()
builder = UnrealMenuBuilder(
    model,
    root_name="Demo",
    to_string_command=partial(action_script, model="menuet.demo:demo_model"),
    parent=unreal.ToolMenus.get().find_menu(unreal.Name("LevelEditor.MainMenu")),
)
builder.build()
