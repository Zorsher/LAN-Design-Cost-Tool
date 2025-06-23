from PySide6 import QtWidgets, QtGui

def load_style():
    with open("gui/style.qss", "r+") as file:
        return file.read()

class Application(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        name = "LAN Design Cost Tool"
        self.setApplicationName(name)
        self.setDesktopFileName(name)
        self.setStyleSheet(load_style())
        self.setWindowIcon(QtGui.QPixmap("gui/pictures/lan-cost-logo.png"))
        