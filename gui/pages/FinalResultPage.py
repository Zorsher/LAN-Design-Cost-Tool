from PySide6 import QtWidgets, QtCore, QtGui
from ..widgets import PushButton, ScrollArea, PictureWidget
from classes import Floor, Room, Item
from utils import VisioTool
import math

INCH_TO_M = 0.0254

class ResultsWidget(QtWidgets.QWidget):
    area_changed = QtCore.Signal(object)
    class RoomResults(QtWidgets.QVBoxLayout):
        area_changed = QtCore.Signal(object)
        def __init__(self, room: Room, multiplier):
            super().__init__()
            self.multiplier = multiplier
            self.tool = VisioTool()
            self.room = room

            self.central_widget = QtWidgets.QWidget()
            self.addWidget(self.central_widget)

            self.core_layout = QtWidgets.QVBoxLayout()
            self.central_widget.setLayout(self.core_layout)

            self.room_name_label = QtWidgets.QLabel(room.name)
            self.room_name_label.setObjectName("bold")
            self.room_name_label.setFont(QtGui.QFont(self.room_name_label.font().family(), 18))

            self.sep_line = QtWidgets.QFrame()
            self.sep_line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
            self.sep_line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
            # self.sep_line.setFixedHeight(1)

            self.core_layout.addWidget(self.room_name_label)
            self.core_layout.addWidget(self.sep_line)

            sum_leight = 0

            for paths in room.calculated_paths:
                for item, leight in paths:
                    try:
                        item: Item
                        _, path = item.tool.master_shapes[item.shape.master_page_ID]

                        if leight == 0:
                            master_item = item
                            master_path = path
                            continue

                        leight = math.ceil(leight*multiplier)
                        # master_item_leight = math.dist(master_item.distance*multiplier)
                        item_leight = math.ceil(item.distance*multiplier)

                        master_item.distance = math.dist(master_item.projecton, master_item.shape.center_x_y)*INCH_TO_M
                        master_item_leight = math.ceil(master_item.distance*multiplier)

                        # print(f"{_l}*{multiplier}/100 = {leight}")
                        sum_leight+=leight

                        connection_items_layout = QtWidgets.QHBoxLayout()

                        master_icon = PictureWidget(master_path, QtCore.QSize(30, 30))
                        icon = PictureWidget(path, QtCore.QSize(30, 30))

                        # leight_label = QtWidgets.QLabel(f"{leight}")

                        connection_items_layout.addWidget(QtWidgets.QLabel(f"Путь от элемента {master_item.name} ({master_item_leight} м.)"))
                        connection_items_layout.addWidget(master_icon)
                        connection_items_layout.addWidget(QtWidgets.QLabel(f"к элементу {item.name} ({item_leight} м.)"))
                        connection_items_layout.addWidget(icon)
                        connection_items_layout.addWidget(QtWidgets.QLabel(f"за расстояние: {leight} м."))
                        # connection_items_layout.addWidget(leight_label)
                        connection_items_layout.addStretch()

                        self.core_layout.addLayout(connection_items_layout)
                    except Exception as e:
                        continue

            for shapes_ids, leight in room.final_nodes_leight.items():
                connection_layout = QtWidgets.QHBoxLayout()

                start_shape, start_shape_picture_path = self.tool.master_shapes[shapes_ids[0]]
                end_shape, end_shape_picture_path  = self.tool.master_shapes[shapes_ids[1]]

                start_icon = PictureWidget(start_shape_picture_path, QtCore.QSize(30, 30))
                end_icon = PictureWidget(end_shape_picture_path, QtCore.QSize(30, 30))

                leight = math.ceil(leight*multiplier)
                room.parent.full_leight+=leight
                # final_nodes_leight_label = QtWidgets.QLabel(f"{leight}")

                connection_layout.addWidget(QtWidgets.QLabel(f"Путь от начального элемента {start_shape.name}"))
                connection_layout.addWidget(start_icon)
                connection_layout.addWidget(QtWidgets.QLabel(f"к конечному элементу {end_shape.name}"))
                connection_layout.addWidget(end_icon)
                connection_layout.addWidget(QtWidgets.QLabel(f"за расстояние: {leight} м."))
                # connection_layout.addWidget(final_nodes_leight_label)
                connection_layout.addStretch()

                self.core_layout.addLayout(connection_layout)

            if sum_leight != 0:
                sum_leight = math.ceil(sum_leight)
                room.parent.full_leight+=sum_leight if room.status != 0 or room.status != 2 else 0
                self.sum_leight_layout = QtWidgets.QHBoxLayout()
                # self.sum_leight_label = QtWidgets.QLabel(f"{sum_leight}")

                self.sum_leight_layout.addWidget(QtWidgets.QLabel(f"Общая длина всех путей внутри помещения: {sum_leight} м."))
                # self.sum_leight_layout.addWidget(self.sum_leight_label)
                self.sum_leight_layout.addStretch()
                self.core_layout.addLayout(self.sum_leight_layout)


            self.full_leight_layout = QtWidgets.QHBoxLayout()

            room_leight = math.ceil(room.full_leight * multiplier)

            # print(f"{room.full_leight}*{multiplier}/100 = {room_leight}")
            # self.full_leight_label = QtWidgets.QLabel(f"{room_leight}")
            
            self.full_leight_layout.addWidget(QtWidgets.QLabel(f"Длина уникального пути внутри помещения: {room_leight} м."))
            # self.full_leight_layout.addWidget(self.full_leight_label)
            self.full_leight_layout.addStretch()

            self.core_layout.addLayout(self.full_leight_layout)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.stacked_layout = QtWidgets.QStackedLayout()
        self.setLayout(self.stacked_layout)

        self.area_continue_widget = QtWidgets.QWidget()
        self.area_continue_layout = QtWidgets.QVBoxLayout()
        self.area_continue_widget.setLayout(self.area_continue_layout)

        self.floor_area_label = QtWidgets.QLabel("Напишите площадь этажа в квадратных метрах")
        self.floor_area_label.setObjectName("bold")

        self.floor_area_input = QtWidgets.QLineEdit()
        self.floor_area_input.setObjectName("red")
        self.floor_area_input.textChanged.connect(self.area_input_changed)
        self.floor_area_input.setPlaceholderText("120 м²")

        self.area_continue_button = PushButton("Продолжить")
        self.area_continue_button.setEnabled(False)
        self.area_continue_button.clicked.connect(self.show_results)

        self.area_continue_layout.addStretch()
        self.area_continue_layout.addWidget(self.floor_area_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.area_continue_layout.addWidget(self.floor_area_input, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.area_continue_layout.addWidget(self.area_continue_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.area_continue_layout.addStretch()

        self.page_widget = QtWidgets.QWidget()
        self.core_layout = QtWidgets.QVBoxLayout()
        self.page_widget.setLayout(self.core_layout)

        self.label_layout = QtWidgets.QHBoxLayout()
        self.page_label = QtWidgets.QLabel("Конечные результаты")
        self.page_label.setObjectName("bold")

        self.label_layout.addWidget(self.page_label, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)


        self.scroll_area = ScrollArea(ignore_scroll_down=True)

        self.core_layout.addLayout(self.label_layout)
        self.core_layout.addWidget(self.scroll_area)

        self.stacked_layout.addWidget(self.area_continue_widget)
        self.stacked_layout.addWidget(self.page_widget)

    def area_input_changed(self, text):
        if self.stacked_layout.currentIndex() != 0:
            return
        
        try:
            area = float(text)
            if area <= 0.0:
                area = 1.0

            self.floor_area_input.setObjectName("type1")
            self.floor_area_input.style().polish(self.floor_area_input)
            self.area_continue_button.setEnabled(True)
        except:
            self.floor_area_input.setObjectName("red")
            self.floor_area_input.style().polish(self.floor_area_input)
            self.area_continue_button.setEnabled(False)
            return

        self.multiplier = math.sqrt(area / self.floor.area)
        # print(f"{self.multiplier} = sqrt({area} / {self.floor.area})")


        
    def load_page(self, floor: Floor):
        self.floor = floor
        self.floor_area_input.setPlaceholderText(f"{self.floor.area*10000}".split(".")[0]) # почему нет?

    def show_results(self):
        self.stacked_layout.setCurrentIndex(1)
        for room in self.floor.rooms:
            if (room.status == 0 or 
                room.status == -1 or
                (room.full_leight == 0 and len(room.calculated_paths) == 0)
                ):
                continue

            room_results = ResultsWidget.RoomResults(room, self.multiplier)
            self.scroll_area.addWidget(room_results)


        final_leight_label = QtWidgets.QLabel(f"ИТОГО: {self.floor.full_leight} + 5% = {math.ceil(self.floor.full_leight+(self.floor.full_leight*0.05))} м.")
        final_leight_label.setObjectName("bold")

        final_leight_layout = QtWidgets.QHBoxLayout()
        final_leight_layout.addSpacing(9)
        final_leight_layout.addWidget(final_leight_label)

        self.scroll_area.addWidget(final_leight_layout)