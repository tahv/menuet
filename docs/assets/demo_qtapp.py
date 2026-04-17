from PySide6 import QtWidgets
from PySide6.QtCore import Qt

from menuet.builders.qt import QMenuBuilder
from menuet.demo import demo_model

app = QtWidgets.QApplication([])
app.setAttribute(
    Qt.ApplicationAttribute.AA_DontShowIconsInMenus,
    on=False,  # show icons on macOS
)
app.setAttribute(
    Qt.ApplicationAttribute.AA_DontUseNativeMenuBar,
    on=False,  # use macOS native menubar
)

model = demo_model()
builder = QMenuBuilder(model, root_menu="Demo")
menu = builder.build()

window = QtWidgets.QMainWindow()
window.menuBar().addMenu(menu)
window.show()

app.exec()
