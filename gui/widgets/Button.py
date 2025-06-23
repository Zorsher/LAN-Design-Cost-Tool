from PySide6 import QtWidgets, QtCore, QtGui
from typing import Union

class PushButton(QtWidgets.QPushButton):
    enterEventRecived = QtCore.Signal(object)
    leaveEventRecived = QtCore.Signal(object)
    def __init__(self, text: str = None, parent = None, icon: QtGui.QIcon = None, CursorShape: QtCore.Qt.CursorShape = QtCore.Qt.CursorShape.PointingHandCursor):
        super().__init__()
        self.setFixedHeight(25)

        self.setText(text) if text != None else ...
        self.setParent(parent) if parent != None else ...
        self.setIcon(icon) if icon != None else ...
        self.setCursor(CursorShape)
        self.setObjectName("type1")

    def changeStyle(self, style: str = None):
        self.setStyleSheet(style) if style != None else ...
        self.style().polish(self)

    def setIcon(self, icon: Union[QtGui.QIcon, QtGui.QPixmap, QtGui.QImage, bytes]):
        if isinstance(icon, bytes):
            data = icon
            icon = QtGui.QImage()
            icon.loadFromData(data)

        if isinstance(icon, Union[QtGui.QImage, QtGui.QPixmap]):
            self.setIconSize(self.size())
            icon = icon.scaled(
                    self.size(),
                    QtCore.Qt.AspectRatioMode.IgnoreAspectRatio,
                    QtCore.Qt.TransformationMode.SmoothTransformation)
            
            rounded = QtGui.QPixmap(self.width(), self.height())
            rounded.fill(QtCore.Qt.GlobalColor.transparent)
            
            path = QtGui.QPainterPath()
            path.addEllipse(0, 0, self.width(), self.height())
            
            painter = QtGui.QPainter(rounded)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            painter.setClipPath(path)
            painter.drawImage(0, 0, icon) if isinstance(icon, QtGui.QImage) else painter.drawPixmap(0, 0, icon)
            painter.end()

            icon = QtGui.QIcon(rounded)

        return super().setIcon(icon)

    def enterEvent(self, event):
        self.enterEventRecived.emit(event)
        return super().enterEvent(event)

    def leaveEvent(self, a0):
        self.leaveEventRecived.emit(a0)
        return super().leaveEvent(a0)

