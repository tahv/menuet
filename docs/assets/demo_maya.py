from menuet.builders.maya import MayaMenuBuilder
from menuet.demo import demo_model

model = demo_model()
builder = MayaMenuBuilder(model, root_menu="Demo", parent="MayaWindow")
builder.build()
