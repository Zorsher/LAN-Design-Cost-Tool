from PySide6 import QtCore, QtGui, QtWidgets
from utils import TempFilesManager, VisioTool
from .pages import GetFilesWidget, ElementsTreeWidget, RoomsStatusWidget, ResultsWidget
from classes import Floor, Room
from vsdx import Shape, Page

INCH_TO_M = 0.0254

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
                    print(e)
                    self.tool._shapes_loaded = False
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

                self.floor = Floor(graph, wall_shape)

                self.third_page.load_page(self.floor, self.inside_items, self.outside_items)

            case 3:
                items = {}
                # создание словаря мастер фигур объеденяющихся вне комнаты
                for index in range(len(self.outside_items) - 1):
                    if index % 2 == 1:
                        continue
                    
                    next_item = self.outside_items[index+1]

                    items.setdefault(next_item, []).append(self.outside_items[index])

                corridors: set[tuple] = set()

                # расчёт всех соединений в комнате
                for room in self.floor.rooms:
                    if room.status == 2:
                        corridors.update(room.graph.nodes)

                    if room.ignore:
                        continue

                    for index in range(len(self.inside_items) - 1):
                        # print(room.name)
                        if index % 2 == 1:
                            continue

                        current_item = self.inside_items[index]
                        next_item = self.inside_items[index + 1]

                        data = room.find_paths_by_shapes_id(current_item.page_id, next_item.page_id)
                        if data is None:
                            continue

                        paths, leight = data
                        # print("papapaths", paths)

                        room.calculated_paths.append(paths)
                        room.full_leight+=leight

                for reference_shape, connected_shapes in items.items():
                    # определение конечной вершины
                    final_node, final_leight = [
                        self.tool.get_minimum_distance_to_graph_nodes(
                            self.floor.G,
                            room.items[reference_shape.page_id][0].projecton,
                            list(corridors)
                        ) 

                        for room in self.floor.rooms 
                        if reference_shape.page_id in room.items and not room.ignore
                        ][0] # вопросы?
                    
                    for connected_shape in connected_shapes:
                        # print(connected_shapes)
                        rooms_nodes: dict[str, list[Room]] = {}
                        
                        # поиск близжайшего расстояния фигур к вершнам многоугольнка коридора
                        for room in self.floor.rooms:
                            if connected_shape.page_id not in room.items:
                                continue

                            if room.ignore:
                                continue

                            item = room.items[connected_shape.page_id][0]

                            room_node, room_leight = self.tool.get_minimum_distance_to_graph_nodes(self.floor.G, item.projecton, list(corridors))

                            room.final_nodes_leight[(reference_shape.page_id, connected_shape.page_id)] = (room_leight + final_leight)

                            rooms_nodes.setdefault(room_node, []).append(room)

                        # поиск путей внутри вершин коридора
                        # its over...
                        nodes, global_path = self.tool.find_minimum_paths_in_graph(self.floor.G, list(rooms_nodes.keys()), final_node)
                        # print(nodes, global_path)

                        for room in self.floor.rooms:
                            if room.status != 2:
                                continue

                            if room.ignore:
                                continue

                            room.calculated_paths.append(nodes)
                            room.full_leight = global_path

                        # добавление длины пути к каждому типу соединения
                        for node, path_leight in nodes:
                            if path_leight == 0:
                                continue

                            for room in rooms_nodes[node]:
                                room.final_nodes_leight[(reference_shape.page_id, connected_shape.page_id)] += path_leight
                                # print(room.full_leight, room.final_nodes_leight)


                
                # for room in self.floor.rooms:
                #     print(room.name, room.calculated_paths, room.full_leight, room.final_nodes_leight)

                self.fourth_page.load_page(self.floor)
                self.central_stacked_layout.setCurrentIndex(3)

    def resizeEvent(self, event):
        self.central_widget.setFixedSize(event.size())
        return super().resizeEvent(event)
    



