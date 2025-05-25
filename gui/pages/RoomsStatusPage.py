from PySide6 import QtWidgets, QtCore, QtGui
from ..widgets import PushButton, ScrollArea, EnteredCombo, MouseWidget, AreaInput
from utils import SignalHandler, VisioTool
from classes import Floor, Room


class RoomsStatusWidget(QtWidgets.QWidget):
    class RoomWidget(QtWidgets.QWidget):
        send_changes = QtCore.Signal(object)
        recieve_changes = QtCore.Signal(object)
        previous_status: str = None

        def __init__(self, room: Room, inside_items, outside_items, parent):
            super().__init__()
            self.parent_: RoomsStatusWidget = parent
            self.room = room
            self.previous_status = 0
            self.inside_items = inside_items
            self.outside_items = outside_items
            self.visiotool = VisioTool()

            self.mouse_widget = MouseWidget()
            self.signal_handler = SignalHandler()
            self.signal_handler.rooms_querry.connect(self.recieve_querry)

            self.combined_items = set()
            self.combined_items.update(inside_items+outside_items)

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
            self.room_name.textChanged.connect(self.room_name_changed)

            self.room_status = QtWidgets.QComboBox()
            self.room_status.addItems(
                ["Отсутствует", "Комната", "Коридор", "Игнорировать комнату"])
            self.room_status.currentTextChanged.connect(self.room_status_changed)

            self.merge_combobox = EnteredCombo()    
            self.merge_combobox.addItem("Пусто", False)        
            self.merge_combobox.entered.connect(self.show_combobox_item)
            self.merge_combobox.mouse_moved.connect(self.move_picture_widget)
            self.merge_combobox.leave_event.connect(self.mouse_widget.hide)
            self.merge_combobox.currentIndexChanged.connect(self.merge_rooms)

            self.merged_rooms_widget = MergedRoomsList()
            self.merged_rooms_widget.setVisible(False)

            self.room_items_layout = QtWidgets.QVBoxLayout()

            for item in self.combined_items:
                if item.page_id in room.items:
                    self.room_items_layout.addWidget(QtWidgets.QLabel(f"{item.name}: {len(room.items[item.page_id])} шт."))


            self.room_status_layout.addStretch()
            self.room_status_layout.addWidget(QtWidgets.QLabel("Название помещения"))
            self.room_status_layout.addWidget(self.room_name)
            self.room_status_layout.addWidget(QtWidgets.QLabel("Статус помещения"))
            self.room_status_layout.addWidget(self.room_status)
            self.room_status_layout.addWidget(QtWidgets.QLabel("Объединить с..."))
            self.room_status_layout.addWidget(self.merge_combobox)
            self.room_status_layout.addWidget(self.merged_rooms_widget)
            self.room_status_layout.addLayout(self.room_items_layout)
            self.room_status_layout.addStretch()

            self.room_status.setCurrentIndex(1 if self.room_items_layout.count() != 0 else 2)

            self.core_layout.addWidget(self.room_picture_widget)
            self.core_layout.addLayout(self.room_status_layout)

        def recieve_querry(self, querry):
            change = querry["change"]

            match change:
                case "name":
                    room = querry["room"]
                    if room is False:
                        # Логика разъеденения?
                        return

                    if room == self:
                        self.room_name.setText(querry["value"])
                        return

                    self.merge_combobox.setItemText(self.merge_combobox.findData(room), querry["value"])

                case "merge":
                    item_to_remove: RoomsStatusWidget.RoomWidget = querry["second_room"]
                    self.merge_combobox.setCurrentIndex(0)

                    if self == item_to_remove:
                        return
                    
                    item_to_remove.room.ignore = True

                    self.merge_combobox.removeItem(self.merge_combobox.findData(item_to_remove))
                    

                case "decouple":
                    # достать класс из self.parent_.rooms_list
                    ...
        
        def room_name_changed(self, name):
            self.room.name = name
            querry = {"change": "name", "room": self, "value": name}
            self.signal_handler.rooms_querry.emit(querry)

        def merge_rooms(self, index):
            if index == 0:
                return

            widget: RoomsStatusWidget.RoomWidget = self.merge_combobox.itemData(index)
            main_room = self.room
            second_room = widget.room
            second_room.ignore = True


            print(main_room.name, second_room.name, main_room.ignore, second_room.ignore)

            picture_path, graph = self.room.parent.merge_rooms(main_room, second_room)

            for index in range(0, self.room_items_layout.count()):
                item = self.room_items_layout.takeAt(0)
                try:
                    w = item.widget()
                    w.deleteLater()
                    self.room_items_layout.removeWidget(w)
                except:
                    ...

            print(self.room_items_layout.count())

            for item in self.combined_items:
                if item.page_id in main_room.items:
                    self.room_items_layout.addWidget(QtWidgets.QLabel(f"{item.name}: {len(main_room.items[item.page_id])} шт."))

            self.room_picture = QtGui.QPixmap(picture_path).scaled(
                QtCore.QSize(540, 360), 
                aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                mode=QtCore.Qt.TransformationMode.SmoothTransformation)
            
            self.background.setPixmap(self.room_picture)

            self.merged_rooms_widget.setVisible(True)
            self.merged_rooms_widget.addRoom(widget)

            if widget.merged_rooms_widget.room_list != 0:
                for room_widget in widget.merged_rooms_widget.room_list:
                    self.merged_rooms_widget.addRoom(room_widget)
          

            querry = {"change": "merge", "first_room": self, "second_room": widget}
            self.signal_handler.rooms_querry.emit(querry)

        def room_status_changed(self):
            current_index = self.room_status.currentIndex()
            self.room.status = self.room_status.currentIndex()
            
            if current_index != 2 and self.previous_status != 2:
                return
            
            if self.previous_status == 2 and current_index == 2:
                return
            
            self.previous_status = current_index

            if current_index == 2:
                self.room.parent.corridor_rooms.append(self.room)
            else:
                self.room.parent.corridor_rooms.remove(self.room)

        def update_picture_widget(self, original_pixmap: QtGui.QPixmap):
            room_picture_widget = QtWidgets.QWidget()
            room_picture_widget.setFixedSize(270, 180)

            background = QtWidgets.QLabel(room_picture_widget)
            room_picture = original_pixmap.copy().scaled(
                QtCore.QSize(270, 180), 
                aspectMode=QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                mode=QtCore.Qt.TransformationMode.SmoothTransformation)
            
            background.setPixmap(room_picture)

            self.mouse_widget.addWidget(room_picture_widget)

        def show_combobox_item(self, *args):
            item: QtCore.QModelIndex = args[0]

            if item.row() == 0:
                self.mouse_widget.hide()
                return
            
            self.update_picture_widget(self.merge_combobox.itemData(item.row()).room_picture)

        def move_picture_widget(self):
            self.cursor_ = QtGui.QCursor()
            if self.mouse_widget.isHidden():
                self.mouse_widget.show()

            self.mouse_widget.move(self.cursor_.pos())

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
        
        def load_items(self):
            for room_item in self.parent_.rooms_list:
                if room_item == self:
                    continue
                self.merge_combobox.addItem(room_item.room_name.text(), room_item)


    test_querry = QtCore.Signal(object)
    room_status_completed = QtCore.Signal(object)
    floor: Floor
    rooms_list: list[RoomWidget]

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
        self.rooms_layout.currentChanged.connect(self.page_changed)

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

    def page_changed(self, index):
        room_widget: RoomsStatusWidget.RoomWidget = self.rooms_list[index]

        self.back_button.setEnabled(False) if self.rooms_list[self.rooms_layout.currentIndex() - 1].room.ignore and self.rooms_layout.currentIndex() - 1 <= 0 else ...

        if room_widget.room.ignore:
            self.change_page(self.sign)

    def change_page(self, sign):
        self.sign = sign

        if sign == "+":
            if self.rooms_layout.currentIndex() + 1 >= len(self.rooms_list):
                self.room_status_completed.emit(self.floor)
                return
            
            self.back_button.setEnabled(True)

            self.rooms_layout.setCurrentIndex(self.rooms_layout.currentIndex() + 1)
            
        else:
            if self.rooms_layout.currentIndex() == 0:
                self.back_button.setEnabled(False)
                return

            self.rooms_layout.setCurrentIndex(self.rooms_layout.currentIndex() - 1)

    def load_page(self, floor, inside_items, outside_items):
        self.floor = floor

        for index, room in enumerate(self.floor.rooms):
            room_widget = RoomsStatusWidget.RoomWidget(room, inside_items, outside_items, self)
            room_widget.send_changes.connect(room_widget.recieve_changes.emit)
            room_widget.room_name.setPlaceholderText(f"Комната {index}")
            room_widget.room_name.setText(f"Комната {index}")
            self.rooms_list.append(room_widget)
            self.rooms_layout.addWidget(room_widget)

        for room_widget in self.rooms_list:
            room_widget.load_items()


class MergedRoomsList(ScrollArea):
    def __init__(self):
        super().__init__(ignore_scroll_down=True, isInverted=True)
        self.scrollLayout.setContentsMargins(0, 5, 5, 0)
        self.room_list: list[RoomsStatusWidget.RoomWidget] = []


    def addRoom(self, room_widget: RoomsStatusWidget.RoomWidget):
        self.room_list.append(room_widget)

        item_layout = QtWidgets.QVBoxLayout()
        item_layout.setContentsMargins(0, 0, 0, 0)

        item_widget = QtWidgets.QWidget()
        item_widget.setFixedHeight(30)
        item_widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        item_widget.setObjectName("border")

        item_widget_layout = QtWidgets.QHBoxLayout()
        item_widget_layout.setContentsMargins(0, 0, 5, 0)
        item_widget.setLayout(item_widget_layout)

        item_name = AreaInput(room_widget.room.name)

        item_widget_layout.addWidget(item_name)

        # delete_button = PushButton(icon=QtWidgets.QApplication.style().standardIcon(QtWidgets.QApplication.style().StandardPixmap.SP_DialogCancelButton))
        # delete_button.setFixedSize(20, 20)
        # delete_button.clicked.connect(lambda item = item_layout, room = room_widget: self.delete_room(item, room))

        # item_widget_layout.addStretch()
        # item_widget_layout.addWidget(delete_button)


        item_layout.addWidget(item_widget)
        self.addWidget(item_layout)

        def enterEvent():
            room_pixmap = QtGui.QPixmap(room_widget.room.room_picture_path)

            room_widget.update_picture_widget(room_pixmap)
            room_widget.move_picture_widget()
            room_widget.mouse_widget.move(room_widget.mouse_widget.pos() + QtCore.QPoint(2, 2))

        def leaveEvent():
            room_widget.mouse_widget.hide()

        def room_name_changed():
            print(item_name.text())
            room_widget.room_name_changed(item_name.text())

        def recieved_querry(querry):
            if querry["change"] != "name":
                return
            
            if querry["room"] != room_widget:
                return
            
            item_name.setText(querry["value"])

        item_name.enter.connect(enterEvent)
        item_name.leave.connect(leaveEvent)
        item_name.textChanged.connect(room_name_changed)
        SignalHandler().rooms_querry.connect(recieved_querry)

    # def delete_room(self, item_widget: QtWidgets.QWidget, room_widget: RoomsStatusWidget.RoomWidget):
    #     ...