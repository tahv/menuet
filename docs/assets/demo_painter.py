import substance_painter.ui

from menuet.builders.qt import QMenuBuilder
from menuet.demo import demo_model

model = demo_model()
menu = QMenuBuilder(model, root_menu="Demo").build()
window = substance_painter.ui.get_main_window()
window.menuBar().addMenu(menu)
