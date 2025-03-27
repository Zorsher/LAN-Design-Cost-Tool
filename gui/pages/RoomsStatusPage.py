from PySide6 import QtWidgets, QtCore, QtGui
from ..widgets import PushButton
from classes import Floor, Room


class RoomsStatusWidget(QtWidgets.QWidget):
    class RoomWidget(QtWidgets.QWidget):
        previous_status: str = None

        def __init__(self, room: Room, inside_items, outside_items):
            super().__init__()
            self.room = room
            self.previous_status = 0
            combined_items = set()
            combined_items.update(inside_items+outside_items)
            # print(combined_items)
            # print(room.items)
            self.core_layout = QtWidgets.QHBoxLayout()
            self.setLayout(self.core_layout)

            self.room_picture_widget = QtWidgets.QWidget()
            self.room_picture_widget.setFixedSize(540, 360)

            self.background = QtWidgets.QLabel(self.room_picture_widget)
            self.room_picture = QtGui.QPixmap(room.room_picture_path).scaled(
                QtCore.QSize(540, 360), 
                aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                mode=QtCore.Qt.TransformationMode.SmoothTransformation)
            
            self.background.setPixmap(self.room_picture)

            self.room_status_layout = QtWidgets.QVBoxLayout()

            self.room_name = QtWidgets.QLineEdit()
            self.room_name.textChanged.connect(lambda text: setattr(room, "name", text))

            self.room_status = QtWidgets.QComboBox()
            self.room_status.addItems(
                ["Отсутствует", "Комната", "Кордиор", "Игнорировать комнату"])
            self.room_status.currentTextChanged.connect(self.room_status_changed)
            
            self.room_status_layout.addStretch()
            self.room_status_layout.addWidget(QtWidgets.QLabel("Название помещения"))
            self.room_status_layout.addWidget(self.room_name)
            self.room_status_layout.addWidget(QtWidgets.QLabel("Статус помещения"))
            self.room_status_layout.addWidget(self.room_status)

            default_widgets_count = self.room_status_layout.count() + 1
            
            for item in combined_items:
                if item.page_id in room.items:
                    self.room_status_layout.addWidget(QtWidgets.QLabel(f"{item.name}: {len(room.items[item.page_id])} шт."))

            self.room_status_layout.addStretch()

            self.room_status.setCurrentIndex(1 if default_widgets_count < self.room_status_layout.count() else 2)

            self.core_layout.addWidget(self.room_picture_widget)
            self.core_layout.addLayout(self.room_status_layout)

        def room_status_changed(self):
            current_index = self.room_status.currentIndex()
            self.room.name = self.room_status.currentText()
            
            if current_index != 2 and self.previous_status != 2:
                return
            
            if self.previous_status == 2 and current_index == 2:
                return
            
            self.previous_status = current_index

            if current_index == 2:
                self.room.parent.corridor_rooms.append(self.room)
            else:
                self.room.parent.corridor_rooms.remove(self.room)
            


        def resizeEvent(self, event):
            try:
                width = int(event.size().width()/1.48)
                height = int(event.size().height()/1.48)

                scaled_pixmap = self.room_picture.scaled(
                    QtCore.QSize(width, height), 
                    aspectMode=QtCore.Qt.AspectRatioMode.IgnoreAspectRatio, 
                    mode=QtCore.Qt.TransformationMode.SmoothTransformation)
                
                self.background.setPixmap(scaled_pixmap)
                self.background.setFixedSize(width, height)
                self.room_picture_widget.setFixedSize(width, height)
            except Exception as e:
                print(e)
            return super().resizeEvent(event)


    room_status_completed = QtCore.Signal(object)
    floor: Floor
    rooms_list: list[Room]

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.rooms_list = []

        self.core_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.core_layout)

        self.label_layout = QtWidgets.QHBoxLayout()
        self.page_label = QtWidgets.QLabel("Напишите название помещения и выберете её принадлежность")
        self.page_label.setObjectName("bold")
        self.label_layout.addWidget(self.page_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        self.rooms_layout = QtWidgets.QStackedLayout()

        self.navigation_buttons_layout = QtWidgets.QHBoxLayout()

        self.back_button = PushButton("Назад...")
        self.back_button.setFixedWidth(100)
        self.back_button.setEnabled(False)
        self.back_button.clicked.connect(lambda _, s = "-": self.change_page(s))

        self.continue_button = PushButton("Далее...")
        self.continue_button.setFixedWidth(100)
        self.continue_button.clicked.connect(lambda _, s = "+": self.change_page(s))

        self.navigation_buttons_layout.addStretch()
        self.navigation_buttons_layout.addWidget(self.back_button)
        self.navigation_buttons_layout.addWidget(self.continue_button)

        self.core_layout.addLayout(self.label_layout)
        self.core_layout.addLayout(self.rooms_layout)
        self.core_layout.addLayout(self.navigation_buttons_layout)


    def change_page(self, sign):
        if sign == "+":
            if len(self.floor.rooms) == self.rooms_layout.currentIndex() + 1:
                print("hi!")
                self.room_status_completed.emit(self.floor)
                return
            
            self.back_button.setEnabled(True) if self.back_button.isEnabled() is False else ...
            self.rooms_layout.setCurrentIndex(self.rooms_layout.currentIndex() + 1)

        else:
            self.back_button.setEnabled(False) if self.rooms_layout.currentIndex() - 1 == 0 else ...
            self.rooms_layout.setCurrentIndex(self.rooms_layout.currentIndex() - 1)


    def load_page(self, floor, inside_items, outside_items):
        self.floor = floor

        for index, room in enumerate(self.floor.rooms):
            room_widget = RoomsStatusWidget.RoomWidget(room, inside_items, outside_items)
            room_widget.room_name.setText(f"Комната {index}")
            self.rooms_list.append(room_widget)
            self.rooms_layout.addWidget(room_widget)

        # self.rw = RoomsStatusWidget.RoomWidget(self.floor.rooms[0], inside_items, outside_items)
        # self.rooms_layout.addWidget(self.rw)



