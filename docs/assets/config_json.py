import json

import menuet
from menuet.builders.text import Render, TextMenuBuilder

document = """
{
    "menu": [
        {
            "label": "Sub-Menu",
            "menu": ["My App"],
            "group": "Separator"
        }
    ],
    "action": [
        {
            "id": "open-gui",
            "label": "Open GUI",
            "cb": "import myapp; myapp.open_gui()",
            "menu": ["My App", "Sub-Menu"]
        },
        {
            "id": "print-hello",
            "label":  "Print Hello",
            "cb": "print('Hello')"
        }
    ]
}
"""

model = menuet.Model()
menuet.loads(document, model, parser=json.loads)

print(TextMenuBuilder(model, root_menu="Example", render=Render.UTF8).build())
