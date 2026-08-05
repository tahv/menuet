from maya import OpenMayaUI
from PySide6 import QtWidgets
from shiboken6 import wrapInstance

from menuet.builders.qt import QMenuBuilder
from menuet.demo import demo_model

model = demo_model()
menu = QMenuBuilder(model, root_menu="Demo").build()

pointer = OpenMayaUI.MQtUtil.mainWindow()
assert pointer is not None
window = wrapInstance(int(pointer), QtWidgets.QMainWindow)
window.menuBar().addMenu(menu)
