from PySide6 import QtWidgets, QtGui
# from utils import TempFilesManager

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
        

    def event(self, a0):  
        if a0.type() == a0.Type.Quit:
            ...
            # TempFilesManager._tempDir.remove()
        return super().event(a0)