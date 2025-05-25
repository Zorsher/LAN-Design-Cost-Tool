from PySide6 import QtWidgets, QtCore, QtGui
from ..widgets import PushButton, ScrollArea, PictureWidget, AreaInput
from classes import Floor, Room, Item
from utils import VisioTool, SignalHandler
from vsdx import Page

import math

INCH_TO_M = 0.0254

class FinalCost(QtWidgets.QHBoxLayout):
    def __init__(self, item: tuple[Page, str], multiplier, index):
        super().__init__()
        self.multiplier = multiplier
        self.item = item
        self.index = index

        if item is not None:
            self.page = item[0]
            self.path = item[1]
            self.icon = PictureWidget(self.path, QtCore.QSize(30, 30))
            self.icon.setFixedSize(30, 30)
            self.addWidget(QtWidgets.QLabel(f"Стоимость элемента {self.page.name} (x{multiplier})"))
            self.addWidget(self.icon)
        else:
            self.addWidget(QtWidgets.QLabel("Стоимость кабеля в бухте"))
            self.multiplier_widget = QtWidgets.QLabel(f"(x{math.ceil(multiplier/100)})")
            self.addWidget(self.multiplier_widget)

            self.coil_box = QtWidgets.QComboBox()
            self.coil_box.addItem("100 м", 100)
            self.coil_box.addItem("305 м", 305)
            self.coil_box.addItem("500 м", 500)
            self.coil_box.addItem("1000 м", 1000)
            self.coil_box.currentIndexChanged.connect(self.coil_box_changed)

            self.addWidget(self.coil_box)

        self.cost_input = AreaInput()
        self.cost_input.setPlaceholderText("10000")

        self.cost_label = QtWidgets.QLabel(f"{self.multiplier*0}")
        self.cost_label.setFixedWidth(70)
        self.cost_input.textChanged.connect(self.cost_changed)


        self.addWidget(QtWidgets.QLabel("составляет"))
        self.addWidget(self.cost_input)
        self.addSpacing(0)
        self.addWidget(QtWidgets.QLabel("Общая стоимость:"))
        self.addSpacing(0)
        self.addWidget(self.cost_label)

        self.addStretch()

    def cost_changed(self, text):
        print(text)
        try:
            cost = int(text)
            if cost <= 0:
                raise

            self.cost_input.setObjectName("type1")
            self.cost_input.style().polish(self.cost_input)

            if self.item is None:
                self.coil_box_changed(self.coil_box.currentIndex())
                return
        except:
            self.cost_input.setObjectName("red")
            self.cost_input.style().polish(self.cost_input)
            return

        final_cost = int(cost*self.multiplier)
        self.cost_label.setText(f"{final_cost}")

        SignalHandler().cost_changed.emit(self.index, final_cost)

    def coil_box_changed(self, index):
        coil = self.coil_box.itemData(index)

        coil_count = math.ceil(self.multiplier / coil)

        self.multiplier_widget.setText(f"(x{(coil_count)})")
        
        try:
            cost_text = int(self.cost_input.text())
            cost = int(coil_count * cost_text)
            self.cost_label.setText(str(cost))
            
            SignalHandler().cost_changed.emit(self.index, cost)
        except:
            self.cost_label.setText("0")


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

            self.room_name_label = QtWidgets.QTextBrowser()
            self.room_name_label.setStyleSheet("""
                border: 0px solid rgba(0, 0, 0, 0.0);
                """)
            self.room_name_label.setText(room.name)
            self.room_name_label.setDisabled(True)
            self.room_name_label.setReadOnly(True)

            if len(room.merged_with) != 0:
                merged_room_name = ", ".join([room.name for room in room.merged_with])
                self.room_name_label.setText(f"{self.room_name_label.toPlainText()}, {merged_room_name}")

            self.room_name_label.setObjectName("bold")
            self.room_name_label.setFont(QtGui.QFont(self.room_name_label.font().family(), 18))

            doc = self.room_name_label.document()
            doc.setTextWidth(600)

            self.room_name_label.setFixedHeight(int(doc.size().height())+5)

            self.core_layout.addWidget(self.room_name_label)

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

        self.floor_area_input = AreaInput()
        self.floor_area_input.textChanged.connect(self.area_input_changed)
        self.floor_area_input.enterPressed.connect(self.show_results)
        self.floor_area_input.setObjectName("red")
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
        if not self.area_continue_button.isEnabled():
            return
        
        overall_items = {}

        self.stacked_layout.setCurrentIndex(1)
        for room in self.floor.rooms:
            if (room.ignore or
                room.status == 0 or 
                room.status == -1 or
                (room.full_leight == 0 and len(room.calculated_paths) == 0) 
                ):
                continue

            for used_item in self.floor.used_items:
                if used_item.page_id not in list(room.items.keys()):
                    continue

                overall_items.setdefault(used_item.page_id, 0)
                overall_items[used_item.page_id] += len(room.items[used_item.page_id])


            room_results = ResultsWidget.RoomResults(room, self.multiplier)
            self.scroll_area.addWidget(room_results)

        print(overall_items)
        final_leight = math.ceil(self.floor.full_leight+(self.floor.full_leight*0.05))
        final_leight_label = QtWidgets.QLabel(f"ИТОГО: {self.floor.full_leight} + 5% = {final_leight} м.")
        final_leight_label.setObjectName("bold")

        final_leight_layout = QtWidgets.QHBoxLayout()
        final_leight_layout.addSpacing(9)
        final_leight_layout.addWidget(final_leight_label)

        cost_items_layout = QtWidgets.QVBoxLayout()
        cost_items_layout.setContentsMargins(QtCore.QMargins(8, 0, 0, 0) + cost_items_layout.contentsMargins())

        self.items_cost = []
        cable_cost = FinalCost(None, final_leight, 0)
        self.items_cost.append(0)
        cost_items_layout.addLayout(cable_cost)

        for index, data in enumerate(overall_items.items(), 1):
            item_id, count = data
            item = self.floor.tool.master_shapes[item_id]
            final_item_cost = FinalCost(item, count, index)
            cost_items_layout.addLayout(final_item_cost)
            self.items_cost.append(0)

        self.final_cost_layout = QtWidgets.QHBoxLayout()

        self.final_cost = QtWidgets.QLabel("0")
        self.final_cost_with_percent = QtWidgets.QLabel("0")

        self.final_cost_layout.addWidget(QtWidgets.QLabel("Конечная стоимость"))
        self.final_cost_layout.addWidget(self.final_cost)
        self.final_cost_layout.addWidget(QtWidgets.QLabel("+ 35% ="))
        self.final_cost_layout.addWidget(self.final_cost_with_percent)
        self.final_cost_layout.addStretch()

        SignalHandler().cost_changed.connect(self.cost_changed)

        self.scroll_area.addWidget(final_leight_layout)
        self.scroll_area.addWidget(cost_items_layout)
        self.scroll_area.addWidget(self.final_cost_layout)

    def cost_changed(self, index, cost):
        self.items_cost[index] = cost
        c = sum(self.items_cost)

        self.final_cost.setText(str(c))
        self.final_cost_with_percent.setText(str(math.ceil(c + (c*0.35))))