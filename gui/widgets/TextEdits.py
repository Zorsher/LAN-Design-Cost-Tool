from PySide6 import QtCore, QtWidgets, QtGui

class MessageInput(QtWidgets.QTextEdit):
    enterPressed = QtCore.Signal(object)
    pastePressed = QtCore.Signal(object)
    def __init__(self):
        super().__init__()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key.Key_Tab:
            return

        if ((e.key() == QtCore.Qt.Key.Key_Return or e.key() == QtCore.Qt.Key.Key_Enter) and e.modifiers() == QtCore.Qt.KeyboardModifier.NoModifier):
            self.enterPressed.emit(True)
            return
        
        if e.key() == QtCore.Qt.Key.Key_V and e.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            self.pastePressed.emit(True)
            return
 
        QtCore.QTimer.singleShot(5, lambda: self.verticalScrollBar().setValue(self.verticalScrollBar().maximum()+50))
        return super().keyPressEvent(e)
    
    def dropEvent(self, e):
        if e.mimeData().hasText() and e.mimeData().hasUrls():
            return
        return super().dropEvent(e)
