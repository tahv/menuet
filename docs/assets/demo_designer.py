import sd

from menuet.builders.qt import QMenuBuilder
from menuet.demo import demo_model

model = demo_model()
menu = QMenuBuilder(model, root_menu="Demo").build()
window = sd.getContext().getSDApplication().getQtForPythonUIMgr().getMainWindow()
window.menuBar().addMenu(menu)
