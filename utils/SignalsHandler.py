from PySide6 import QtCore

class SignalHandler():
    _instance = None

    class Signals(QtCore.QObject):
        rooms_querry = QtCore.Signal(object)
        cost_changed = QtCore.Signal(int, object)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = cls.Signals()
        return cls._instance