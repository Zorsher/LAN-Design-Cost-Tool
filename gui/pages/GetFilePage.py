from PySide6 import QtWidgets, QtCore, QtGui
from ..widgets import PushButton


class GetFilesWidget(QtWidgets.QWidget):
    add_file_check = QtCore.Signal(str)
    file_denied = QtCore.Signal()

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.file_denied.connect(self.add_file_denied)
        self.core_layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel("Добавьте ваш файл")

        self.add_file = PushButton("Добавить файл")
        self.add_file.setFixedHeight(30)
        self.add_file.clicked.connect(self.add_file_clicked)


        self.core_layout.addStretch()
        self.core_layout.addWidget(self.label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.core_layout.addSpacing(10)
        self.core_layout.addWidget(self.add_file, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.core_layout.addStretch()

        self.setLayout(self.core_layout)


    def add_file_clicked(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(filter="(*vsdx)")
        if file_path == "":
            return
        
        self.add_file.setEnabled(False)
        self.add_file_check.emit(file_path[0])

    def add_file_denied(self):
        self.label.setText("Файл повреждён или его формат не соотвествует требуемому!")
        self.add_file.setEnabled(True)

    