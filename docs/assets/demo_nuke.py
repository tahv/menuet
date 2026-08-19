import nuke

from menuet.builders.nuke import NukeMenuBuilder
from menuet.demo import demo_model

model = demo_model()
builder = NukeMenuBuilder(
    model,
    root_menu="Demo",
    parent=nuke.toolbar("Nuke"),
    get_shortcut=lambda item: item.extra.get("nuke-shortcut"),
)
builder.build()
