from typing import cast

import pyfbsdk
from PySide6 import QtWidgets
from shiboken6 import wrapInstance

from menuet.builders.qt import QMenuBuilder
from menuet.demo import demo_model


def get_motionbuiler_main_qmenubar() -> QtWidgets.QMenuBar:
    ptr = pyfbsdk.FBGetMainWindow()
    if ptr is None:
        msg = "Can't find MotionBuilder main window"
        raise RuntimeError(msg)

    window = cast("QtWidgets.QMainWindow", wrapInstance(ptr, QtWidgets.QMainWindow))

    # MotionBuilder main QMenuBar is not a direct child of its QMainWindow
    stack = window.children()
    while stack:
        widget = stack.pop(0)  # breadth-first search
        if isinstance(widget, QtWidgets.QMenuBar):
            return widget
        stack.extend(widget.children())

    msg = "Can't find any QMenuBar in MotionBuilder main window hierarchy"
    raise RuntimeError(msg)


model = demo_model()
menu = QMenuBuilder(model, root_menu="Demo").build()
menu_bar = get_motionbuiler_main_qmenubar()
menu_bar.addMenu(menu)
