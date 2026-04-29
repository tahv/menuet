import bpy

from menuet.builders.blender import BlenderMenuBuilder
from menuet.demo import demo_model

model = demo_model()
builder = BlenderMenuBuilder(model, root_menu="Demo")
menu = builder.build()


def menu_draw(self: bpy.types.Menu, context: bpy.types.Context) -> None:
    self.layout.menu(menu.bl_idname)


bpy.types.TOPBAR_MT_editor_menus.append(menu_draw)
