import math
import uuid
import networkx as nx
from vsdx import Shape, Page
from utils import VisioTool
from networkx import Graph

INCH_TO_M = 0.0254
ROUND = 2

class Item():
    shape: Shape
    projecton: tuple
    distance: float
    name: str

    def __init__(self, shape: Shape, projection: list, distance: float):
        self.tool = VisioTool()
        self.shape = shape
        self.projecton = projection
        self.distance = distance
        self.name = self.tool.get_shape_name_by_id(self.shape.master_page_ID)

    def __repr__(self):
        return f"Name: {self.name}, ID: {self.shape.ID}, Original pos: {self.shape.center_x_y}, Projection: {self.projecton}"


class Room():
    ID: int
    name: str
    status: str
    graph: Graph
    items: dict[str, list[Item]]
    reference_nodes: list # Что если их несколько?
    additional_nodees: list[tuple]
    room_picture_path: str
    full_leight: int = 0
    final_nodes_leight: dict[tuple, int]
    calculated_paths: list = None


    
    def __init__(self, graph: list, parent):
        self.parent: Floor = parent
        self.ID = uuid.uuid4()
        self.items = {}
        self.final_nodes_leight = {}
        self.reference_nodes = []
        self.calculated_paths = []
        self.tool = VisioTool()
        self.graph = graph

        self.room_picture_path = self.tool.save_graph_with_highlighted_edges(str(self.ID), parent.G, self.graph.edges)

        shapes_inside = self.tool.get_shapes_inside_polygon(parent.wall_shape, self.graph)
        # print(self.graph.edges)

        for key, values in shapes_inside.items():
            for value in values:
                projection, previous_node, next_node, distance = self.tool.get_minimum_shape_distance_inside_polygon(value, self.graph)
                # print(self.tool.get_shape_name_by_id(value.master_page_ID), projection, previous_node, next_node)
                item = Item(value, projection, distance)

                self.graph.remove_edge(previous_node, next_node)
                self.graph.add_edge(previous_node, projection, weight=math.dist(previous_node, projection) * INCH_TO_M)
                self.graph.add_edge(next_node, projection, weight=math.dist(projection, next_node) * INCH_TO_M)

                if key not in self.items:
                    self.items[key] = [item]
                else:
                    self.items[key].append(item)


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

        paths, leight = self.tool.find_minimum_paths_in_graph(self.graph, start_nodes, end_node)

        start_items.append(end_item)

        for path in paths:
            node = path[0]
            for item in start_items:
                item.name = VisioTool().master_shapes[item.shape.master_page_ID][0].name
                if item.projecton != node:
                    continue

                paths[paths.index(path)][0] = item
                start_items.remove(item)
                break

        return paths, leight




class Floor():
    ID: int
    rooms: list[Room] = []
    corridor_rooms: list[Room] = []
    area: float
    wall_shape: Page
    full_leight: int = 0

    def __init__(self, graph, wall_shape):
        self.tool = VisioTool()
        self.wall_shape = wall_shape

        self.graph = graph
        if isinstance(self.graph, dict):
            self.G = nx.Graph()
            for node, neighbors in self.graph.items():
                for neighbor, weight in neighbors.items():
                    try:
                        weight = weight["weight"]
                    except:
                        pass
                    
                    self.G.add_edge(node, neighbor, weight = weight * INCH_TO_M)
        else:
            self.G = graph

        self.area = 0.0

        for room in nx.minimum_cycle_basis(self.G):
            room_graph = nx.Graph()
            len_room = len(room)
            area = 0

            for i in range(len_room):
                area += room[i][0] * room[(i + 1) % len_room][1] - room[(i + 1) % len_room][0] * room[i][1]
                room_graph.add_edge(room[i], room[(i + 1) % len_room], weight=self.G[room[i]][room[(i + 1) % len_room]]["weight"])

            print(abs(area)*0.00064516)

            area = abs(area)

            self.area+=(area*0.00064516)

            room = Room(room_graph, self)
            self.rooms.append(room)

        self.area*=0.5
        


        print(self.area)
    def find_outside_paths(self, outside_items):
        print(outside_items)




# class Building():
#     floors: list[Floor]

#     def __init__(self, graph: dict):
#         # Пройтись по каждому уникальному
#         ...

