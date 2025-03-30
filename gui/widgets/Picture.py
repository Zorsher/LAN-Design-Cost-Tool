from PySide6 import QtWidgets, QtCore, QtGui

class PictureWidget(QtWidgets.QWidget):
    def __init__(self, picture_path, size: QtCore.QSize = None):
        super().__init__()

        background = QtWidgets.QLabel(self)
        picture = QtGui.QPixmap(picture_path)
        if size is not None:
            picture = picture.scaled(
                size, 
                aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio, 
                mode=QtCore.Qt.TransformationMode.SmoothTransformation
            )

        size = picture.size() if size is None else size
        self.setFixedSize(size)
        background.setFixedSize(size+QtCore.QSize(5, 5))
        background.setPixmap(picture)
