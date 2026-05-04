import pymxs

from menuet.builders.max import MaxDynamicMenuBuilder
from menuet.demo import demo_model

model = demo_model()
builder = MaxDynamicMenuBuilder(model, root_menu="Demo")
builder.build()

# force a reloading of the menu system
config = pymxs.runtime.maxops.GetICuiMenuMgr().GetCurrentConfiguration()
pymxs.runtime.maxops.GetICuiMenuMgr().LoadConfiguration(config)
