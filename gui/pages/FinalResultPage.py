from PySide6 import QtWidgets, QtCore, QtGui
from ..widgets import PushButton

class ResultsWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)