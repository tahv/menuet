import menuet
from menuet.builders.text import Render, TextMenuBuilder

model = menuet.Model()
model.add_menu(
    menuet.Menu(
        label="Sub-Menu",
        menu=["My App"],
        group="Separator",
    )
)
model.add_action(
    menuet.Action(
        id="open-gui",
        label="Open GUI",
        cb="import myapp; myapp.open_gui()",
        menu=["My App", "Sub-Menu"],
    )
)
model.add_action(
    menuet.Action(
        id="print-hello",
        label="Print Hello",
        cb='print("Hello")',
    )
)

print(TextMenuBuilder(model, root_menu="Example", render=Render.UTF8).build())
