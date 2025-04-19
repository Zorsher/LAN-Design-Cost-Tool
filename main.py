from utils import *
from classes import Floor
from vsdx import Page, Shape
from gui import MainWindow, Application

def main():
    import sys
    tmp = TempFilesManager()

    app = Application([])

    gui = MainWindow()
    gui.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()