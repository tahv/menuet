import unreal

from menuet.builders.unreal import UnrealMenuBuilder, model_reference_to_string_command
from menuet.demo import demo_model

tool_menus = unreal.ToolMenus.get()
model = demo_model()
builder = UnrealMenuBuilder(
    model,
    root_name="Demo",
    to_string_command=model_reference_to_string_command("menuet.demo:demo_model"),
    parent=tool_menus.find_menu(unreal.Name("LevelEditor.MainMenu")),
)
builder.build()
