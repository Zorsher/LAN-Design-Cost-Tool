import uuid

from PySide6 import QtWidgets, QtCore, QtGui
from ..widgets import PushButton, ScrollArea
from utils import VisioTool, TempFilesManager

class ElementsTreeWidget(QtWidgets.QWidget):
    class ElementWidget(QtWidgets.QVBoxLayout):
        id: int = 0
        to_delete = QtCore.Signal(object)
        new_connections = QtCore.Signal(list)
        
        def __init__(self, is_inside):
            super().__init__()
            self.is_inside = is_inside
            self.id = uuid.uuid4()

            self.central_widget = QtWidgets.QWidget()
            self.addWidget(self.central_widget)

            self.central_widget.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
            self.central_widget.setObjectName("border")

            self.tool = VisioTool()
            self.temp = TempFilesManager()
            
            self.central_widget.setFixedHeight(60)
            
            self.core_layout = QtWidgets.QHBoxLayout()

            self.from_shape_combobox = QtWidgets.QComboBox()
            self.from_shape_combobox.currentIndexChanged.connect(self.change_shapes_connections)
            self.from_shape_combobox.setFixedHeight(40)
            self.from_shape_combobox.setIconSize(QtCore.QSize(35, 35))

            self.to_shape_combobox = QtWidgets.QComboBox()
            self.to_shape_combobox.currentIndexChanged.connect(self.change_shapes_connections)
            self.to_shape_combobox.setFixedHeight(40)
            self.to_shape_combobox.setIconSize(QtCore.QSize(35, 35))

            self.delete_element_button = PushButton(icon=QtWidgets.QApplication.style().standardIcon(QtWidgets.QApplication.style().StandardPixmap.SP_DialogCancelButton))
            # self.delete_element_button.clicked.connect(lambda: self.to_delete.emit(self))

            for shape, path in self.tool.master_shapes.values():
                icon = QtGui.QPixmap(path)
                self.from_shape_combobox.addItem(icon, shape.name, shape)
                self.to_shape_combobox.addItem(icon, shape.name, shape)

            self.core_layout.addStretch()
            self.core_layout.addWidget(QtWidgets.QLabel("От объекта"), alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
            self.core_layout.addStretch()
            self.core_layout.addWidget(self.from_shape_combobox)
            self.core_layout.addStretch()
            self.core_layout.addWidget(QtWidgets.QLabel("к объекту"))
            self.core_layout.addStretch()
            self.core_layout.addWidget(self.to_shape_combobox)
            self.core_layout.addStretch()
            self.core_layout.addWidget(self.delete_element_button)

            self.central_widget.setLayout(self.core_layout)

        def change_shapes_connections(self):
            self.new_connections.emit(
                (
                self.id,
                "inside" if self.is_inside else "outside",
                self.from_shape_combobox.itemData(self.from_shape_combobox.currentIndex()),
                self.to_shape_combobox.itemData(self.to_shape_combobox.currentIndex())
                )
            )
                
    blacklist: list
    elements_list: dict
    send_shapes = QtCore.Signal(object)
    wall_shape_changed = QtCore.Signal(object)

    def __init__(self, parent):
        super().__init__(parent=parent)
        self.blacklist = []
        self.elements_list = {}
        self.core_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.core_layout)

    def load_page(self):
        self.tool = VisioTool()

        # Блок кода выбора фигуры стены
        self.wall_widget = QtWidgets.QWidget()
        self.wall_widget.setFixedHeight(60)
        self.wall_widget.setObjectName("border")

        self.wall_layout = QtWidgets.QHBoxLayout()
        self.wall_widget.setLayout(self.wall_layout)

        self.wall_label = QtWidgets.QLabel("Выбирете фигуру стены")
        self.wall_label.setObjectName("bold")

        self.wall_combobox = QtWidgets.QComboBox()
        self.wall_combobox.currentIndexChanged.connect(self.wall_update)
        self.wall_combobox.setFixedHeight(40)
        self.wall_combobox.setIconSize(QtCore.QSize(35, 35))

        for shape, path in self.tool.master_shapes.values():
            icon = QtGui.QPixmap(path)
            self.wall_combobox.addItem(icon, shape.name, shape)

        self.wall_shape = self.wall_combobox.itemData(0)

        self.wall_layout.addWidget(self.wall_label)
        self.wall_layout.addStretch()
        self.wall_layout.addSpacing(10)
        self.wall_layout.addWidget(self.wall_combobox)

        self.core_layout.addWidget(self.wall_widget)
        self.core_layout.addSpacing(10)

        # Блок кода выбора структуры соединений
        self.elements_label = QtWidgets.QLabel("Выбирете подключаемые элементы.")
        self.elements_label.setObjectName("bold")

        self.scroll_area = ScrollArea(isInverted=True)
    
        self.elements_buttons_layout = QtWidgets.QHBoxLayout()

        self.add_inside_room_button = PushButton("Объеденить элементы внутри комнаты")
        self.add_inside_room_button.clicked.connect(lambda _, i = True: self.add_element(i))
        self.add_inside_room_button.setFixedHeight(40)

        self.add_outside_room_button = PushButton("Объеденить элементы вне комнаты")
        self.add_outside_room_button.clicked.connect(lambda _, i = False: self.add_element(i))
        self.add_outside_room_button.setFixedHeight(40)

        self.elements_buttons_layout.addWidget(self.add_inside_room_button)
        self.elements_buttons_layout.addWidget(self.add_outside_room_button)

        self.scroll_area.addWidget(self.elements_buttons_layout)

        self.continue_button_layout = QtWidgets.QHBoxLayout()

        self.continue_button = PushButton("Продолжить")
        self.continue_button.clicked.connect(self.continue_clicked)
        self.continue_button.setEnabled(False)
        self.continue_button.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.continue_button.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)

        self.continue_button_layout.addStretch()
        self.continue_button_layout.addWidget(self.continue_button)

        self.core_layout.addWidget(self.elements_label, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        self.core_layout.addSpacing(5)
        self.core_layout.addWidget(self.scroll_area)
        self.core_layout.addLayout(self.continue_button_layout)
        # self.core_layout.addStretch()

    def wall_update(self, id):
        self.wall_shape = self.wall_combobox.itemData(id)
        self.wall_shape_changed.emit(self.wall_shape)

    def add_element(self, is_inside):
        element = ElementsTreeWidget.ElementWidget(is_inside)
        element.new_connections.connect(self.shapes_pair_changed)
        element.new_connections.emit(
            (
            element.id,
            is_inside,
            element.from_shape_combobox.itemData(element.from_shape_combobox.currentIndex()),
            element.to_shape_combobox.itemData(element.to_shape_combobox.currentIndex())
            )
        )

        element.delete_element_button.clicked.connect(lambda _, w = element: self.del_element(w))
        self.scroll_area.addWidget(element, index=1)

        self.continue_button.setEnabled(True) if self.continue_button.isEnabled() is None else ...

    def shapes_pair_changed(self, data: list):
        self.continue_button.setEnabled(True)
        element_id = data[0]
        element_type = data[1]
        shape_from = data[2]
        shape_to = data[3]
        # print("ha", shape_from, shape_to)

        self.elements_list[element_id] = [element_type, shape_from, shape_to]


    def del_element(self, widget: QtWidgets.QBoxLayout):
        # print(self.elements_list)
        self.elements_list.pop(widget.id)
        self.scroll_area.delWidget(widget)
        if len(self.elements_list) == 0:
            self.continue_button.setEnabled(False)

    def continue_clicked(self):
        connections = {"wall": self.wall_shape, "inside": [], "outside": []}
        # print("elements", self.elements_list)
        for id, data in self.elements_list.items():
            element_type = data[0]
            shape_from = data[1]
            shape_to = data[2]
            # print("данные", f"id: {id}, shape_from: {shape_from}, shape_to: {shape_to}")

            if element_type not in connections:
                connections[element_type] = [shape_from, shape_to]
            else:
                connections[element_type].extend((shape_from, shape_to))

        self.send_shapes.emit(connections)

