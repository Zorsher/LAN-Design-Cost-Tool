from PySide6 import QtWidgets, QtCore, QtGui


class EnteredView(QtWidgets.QListView):
    moved = QtCore.Signal(object)
    leave_event = QtCore.Signal(object)
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.last_pos = QtCore.QPoint(0, 0)

    def mouseMoveEvent(self, e):
        self.last_pos = e.pos()
        self.moved.emit(e.pos())
        return super().mouseMoveEvent(e)
    
    def leaveEvent(self, event):
        last_pos_x = self.last_pos.x()
        last_pos_y = self.last_pos.y()

        height = self.size().height()
        width = self.size().width()

        if ((last_pos_x >= width-7 or last_pos_x == 0) or 
            (last_pos_y >= height-7 or last_pos_y == 0)):
            self.leave_event.emit(event)

        return super().leaveEvent(event)
    
    def event(self, e):
        if e.type().name == "Hide":
            self.leave_event.emit(e)
        return super().event(e)
        


class EnteredCombo(QtWidgets.QComboBox):
    entered = QtCore.Signal(object)
    mouse_moved = QtCore.Signal(object)
    leave_event = QtCore.Signal(object)
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)

        view = EnteredView()
        view.leave_event.connect(self.leave_event.emit)
        self.setView(view)

        view.moved.connect(self.mouse_moved.emit)
        view.entered.connect(self.entered.emit)
