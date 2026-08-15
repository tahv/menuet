from menuet.builders.maya import (
    MayaMarkingMenuBuilder,
    MayaMarkingMenuModifier,
    MayaMarkingMenuMouseButton,
)
from menuet.demo import demo_model

model = demo_model()
builder = MayaMarkingMenuBuilder(
    model,
    name="Demo",
    button=MayaMarkingMenuMouseButton.LEFT,
    modifier=MayaMarkingMenuModifier.CTRL | MayaMarkingMenuModifier.SHIFT,
    parent="viewPanes",
    get_rp=lambda item: item.extra.get("radial-position"),
)
builder.build()
