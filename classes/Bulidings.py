import math
import uuid
import matplotlib.pyplot as plt
import networkx as nx
from vsdx import Shape
from utils import VisioTool
from networkx import Graph

INCH_TO_CM = 2.54
ROUND = 2

class Item():
    shape: Shape
    projecton: tuple
    distance: float

    def __init__(self, shape: Shape, projection: list, distance: float):
        self.tool = VisioTool()
        self.shape = shape
        self.projecton = projection
        self.distance = distance

    def __repr__(self):
        return f"Name: {self.tool.get_shape_name_by_id(self.shape.master_page_ID)}, ID: {self.shape.ID}, Original pos: {self.shape.center_x_y}, Projection: {self.projecton}"


class Room():
    ID: int
    name: str
    status: str
    graph: Graph
    items: dict[str, list[Item]]
    reference_node: tuple # Что если их несколько?
    additional_nodees: list[tuple]
    room_picture_path: str
    full_leight: int = None
    calculated_paths: tuple = None

    
    def __init__(self, graph: list, parent):
        self.ID = uuid.uuid4()
        self.parent: Floor = parent
        self.items = {}
        self.tool = VisioTool()
        self.graph = graph

        self.room_picture_path = self.tool.save_graph_with_highlighted_edges(str(self.ID), parent.G, self.graph.edges)

        shapes_inside = self.tool.get_shapes_inside_polygon(self.graph)
        # print(self.graph.edges)

        for key, values in shapes_inside.items():
            for value in values:
                projection, previous_node, next_node, distance = self.tool.get_minimum_shape_distance_inside_polygon(value, self.graph)
                # print(self.tool.get_shape_name_by_id(value.master_page_ID), projection, previous_node, next_node)
                item = Item(value, projection, distance)

                self.graph.remove_edge(previous_node, next_node)
                self.graph.add_edge(previous_node, projection, weight=round(math.dist(previous_node, projection) * INCH_TO_CM, ROUND))
                self.graph.add_edge(next_node, projection, weight=round(math.dist(projection, next_node) * INCH_TO_CM, ROUND))

                if key not in self.items:
                    self.items[key] = [item]
                else:
                    self.items[key].append(item)

    def has_server(self):
        ID = self.tool.get_shape_id_by_name("Server")
        return str(ID) in self.items
            

    # def find_paths_by_shapes_id(self, start_shape_id: int, end_shape_id: int):
    #     """
    #     Находит единый путь в заданном графе от начальных вершин до конечной вершины.
    #     Для start_shape_id будут найдены все имеющиеся в графе вершины, которые соответствуют этому ID.

    #     :param: start_shape_id: int - ID начальной вершины.
    #     :param: end_shape_id: int - ID конечной вершины.
    #     """

    #     if str(start_shape_id) not in list(self.items.keys()) or str(end_shape_id) not in list(self.items.keys()):
    #         return

    #     start_nodees = [item.projecton for item in self.items[str(start_shape_id)]]
    #     end_node = self.items[str(end_shape_id)][0].projecton

    #     global_leight = 0
    #     next_node = end_node
    #     visited = [next_node]
    #     paths = [(next_node, 0)]

    #     for i in range(len(start_nodees)):
    #         nearest_nodees = [(node, nx.dijkstra_path_length(self.graph, node, next_node)) for node in start_nodees if node not in visited]
    #         nearest_nodees.sort(key = lambda items: items[-1])

    #         nearest_node, nearest_leight = nearest_nodees[0]
    #         end_leight = nx.dijkstra_path_length(self.graph, nearest_node, end_node)

    #         if nearest_leight <= end_leight:
    #             global_leight+= nearest_leight
    #             leight = nearest_leight+paths[i][-1]
    #         else:
    #             global_leight+= end_leight
    #             leight = end_leight

    #         visited.append(nearest_node)
    #         paths.append((nearest_node, leight))
    #         next_node = nearest_node

    #     # print(paths, global_leight)

    def find_paths_by_shapes_id(self, start_shape_id: int, end_shape_id: int):
        """
        Находит единый путь в заданном графе от начальных вершин до конечной вершины.
        Для start_shape_id будут найдены все имеющиеся в графе вершины, которые соответствуют этому ID.

        :param: start_shape_id: int - ID начальной вершины.
        :param: end_shape_id: int - ID конечной вершины.
        """

        if str(start_shape_id) not in list(self.items.keys()) or str(end_shape_id) not in list(self.items.keys()):
            return

        start_items = [item for item in self.items[str(start_shape_id)]]
        end_item = self.items[str(end_shape_id)][0]

        start_nodes = [item.projecton for item in start_items]
        end_node = end_item.projecton

        # соотнести пути с фигурами
        paths, leight = self.tool.find_minimum_paths_in_graph(self.graph, start_nodes, end_node)

        start_items.append(end_item)

        for path in paths:
            node = path[0]
            for item in start_items:
                if item.projecton == node:
                    paths[paths.index(path)][0] = item
                    start_items.remove(item)
                    break

        return paths, leight




class Floor():
    ID: int
    rooms: list[Room] = []
    corridor_rooms: list[Room] = []

    def __init__(self, graph):
        self.tool = VisioTool()
        self.graph = graph

        self.G = nx.Graph()
        for node, neighbors in self.graph.items():
            for neighbor, weight in neighbors.items():
                self.G.add_edge(node, neighbor, weight = round(weight * INCH_TO_CM, 5))


        for room in nx.minimum_cycle_basis(self.G):
            room_graph = nx.Graph()
            for i in range(len(room)):
                room_graph.add_edge(room[i], room[i - 1], weight=self.G[room[i]][room[i - 1]]["weight"])

            # self.tool.draw_graph_with_highlighted_edges(self.G, room_graph.edges)
            room = Room(room_graph, self)

            # room.room_picture_path = path

            # if room.items

            # room.find_paths_by_shapes_id(9, 10)
            # print("=========")
            # print(room_graph.edges) 
            # print(room.items)
            self.rooms.append(room)

    def find_outside_paths(self, outside_items):
        print(outside_items)




# class Building():
#     floors: list[Floor]

#     def __init__(self, graph: dict):
#         # Пройтись по каждому уникальному
#         ...

