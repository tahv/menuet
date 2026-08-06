import menuet
from menuet.builders.text import Render, TextMenuBuilder

config = {
    "menu": [
        {
            "label": "Sub-Menu",
            "menu": ["My App"],
            "group": "Separator",
        },
    ],
    "action": [
        {
            "id": "open-gui",
            "label": "Open GUI",
            "cb": "import myapp; myapp.open_gui()",
            "menu": ["My App", "Sub-Menu"],
        },
        {
            "id": "print-hello",
            "label": "Print Hello",
            "cb": 'print("Hello")',
        },
    ],
}

model = menuet.Model()
menuet.deserialize(config, model)

print(TextMenuBuilder(model, root_menu="Example", render=Render.UTF8).build())
