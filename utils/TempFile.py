from PySide6 import QtCore, QtGui
from typing import List
import json
import os

class TempFilesManager:
    _instance = None

    def __new__(cls):
        if cls._instance == None:
            cls._tempDir = QtCore.QTemporaryDir()
            print(cls._tempDir.path())
            cls._tempDir.setAutoRemove(True)

            cls._tempFile = QtCore.QTemporaryFile()
            cls._tempFile.setAutoRemove(True)
            if cls._tempFile.open(QtCore.QIODeviceBase.OpenModeFlag.WriteOnly):
                cls._tempFile.write(json.dumps({}).encode())
                cls._tempFile.close()

            cls._instance = super().__new__(cls)
        return cls._instance

    
    def dump(self, data):
        if self._tempFile.open(QtCore.QIODevice.OpenModeFlag.WriteOnly | QtCore.QIODevice.OpenModeFlag.Truncate):
            self._tempFile.resize(0)
            self._tempFile.writeData(json.dumps(data).encode())
            self._tempFile.flush()
            self._tempFile.close()

    def load(self) -> dict:
        if self._tempFile.open(QtCore.QIODeviceBase.OpenModeFlag.ReadOnly):
            try:
                data = json.loads(self._tempFile.readAll().data().decode())
                self._tempFile.close()
                return data
            except Exception as e:
                print(e)

    def get_shapes_pictures_list(self):
        return os.listdir(self._tempDir.path())