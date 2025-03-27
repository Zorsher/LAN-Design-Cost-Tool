from PySide6 import QtCore, QtGui, QtWidgets
from utils import TempFilesManager, VisioTool
from .pages import GetFilesWidget, ElementsTreeWidget, RoomsStatusWidget, ResultsWidget
from classes import Floor
from vsdx import Shape, Page

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)

        self.central_widget = QtWidgets.QWidget(self)
        self.central_stacked_layout = QtWidgets.QStackedLayout(self.central_widget)

        self.first_page = GetFilesWidget(self)
        self.first_page.add_file_check.connect(lambda path: self.change_page(1, path))
        self.first_page.setStyleSheet(self.styleSheet())

        self.second_page = ElementsTreeWidget(self)
        self.second_page.send_shapes.connect(lambda data: self.change_page(2, data))
        self.second_page.setStyleSheet(self.styleSheet())

        self.third_page = RoomsStatusWidget(self)
        self.third_page.room_status_completed.connect(lambda data: self.change_page(3, data))

        self.fourth_page = ResultsWidget(self)

        self.central_stacked_layout.addWidget(self.first_page)
        self.central_stacked_layout.addWidget(self.second_page)
        self.central_stacked_layout.addWidget(self.third_page)
        self.central_stacked_layout.addWidget(self.fourth_page)

    def change_page(self, index, data):
        match index:
            case 1:
                try:
                    self.tool = VisioTool(data)
                except Exception as e:
                    # self.tool._isinstance = None
                    self.first_page.file_denied.emit()
                    return
                       
                self.second_page.load_page()

                self.temp = TempFilesManager()
                self.central_stacked_layout.setCurrentIndex(1)

            case 2:
                # print(data)
                wall_shape = data["wall"]
                self.inside_items: list[Page] = data["inside"]
                self.outside_items: list[Page] = data["outside"]
                # print(inside_items, outside_items)

                self.central_stacked_layout.setCurrentIndex(2)
                shapes = self.tool.get_shapes_by_id(wall_shape.page_id)
                graph = self.tool.get_shapes_connections(shapes)

                self.floor = Floor(graph)

                self.third_page.load_page(self.floor, self.inside_items, self.outside_items)

            case 3:
                print("in", self.inside_items)
                items = {}
                for index in range(len(self.outside_items) - 1):
                    if index % 2 == 1:
                        continue
                    
                    next_item = self.outside_items[index+1]

                    if next_item in items:
                        items[next_item].append(self.outside_items[index])
                    else:
                        items[next_item] = self.outside_items[index]

                for room in self.floor.rooms:
                    for index in range(len(self.inside_items) - 1):
                        if index % 2 == 1:
                            continue

                        current_item = self.inside_items[index]
                        next_item = self.inside_items[index + 1]

                        data = room.find_paths_by_shapes_id(current_item.page_id, next_item.page_id)
                        if data is None:
                            continue

                        paths, leight = data

                        room.calculated_paths = paths
                        room.full_leight = leight

                for room in self.floor.rooms:
                    print(room.calculated_paths, room.full_leight)


                self.central_stacked_layout.setCurrentIndex(3)






    def resizeEvent(self, event):
        self.central_widget.setFixedSize(event.size())
        return super().resizeEvent(event)
    



