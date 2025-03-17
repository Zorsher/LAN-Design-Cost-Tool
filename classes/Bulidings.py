from vsdx import Shape
import networkx as nx
from visio import VisioTool

class Item():
    shape: Shape
    projecton: list
    distance: float

    def __init__(self, shape: Shape, projection: list, distance: float):
        self.tool = VisioTool()
        self.shape = shape
        self.projecton = projection
        self.distance = distance

    def __repr__(self):
        return f"Name: {self.tool.get_shape_name_by_id(self.shape.master_page_ID)}, ID: {self.shape.ID}, Original pos: {self.shape.center_x_y}, Projection: {self.projecton}, Distance: {self.distance}"


class Room():
    ID: int
    name: str
    vertexes: list
    items: dict[str, list[Shape]] = {}
    
    def __init__(self, vertexes: list, parent):
        self.tool = VisioTool()
        vertexes.append(vertexes[0])
        self.vertexes = vertexes
        shapes_inside = self.tool.get_shapes_inside_polygon(vertexes)

        for key, values in shapes_inside.items():
            for value in values:
                projection, distance = self.tool.get_minimum_shape_distance_inside_polygon(value, self.vertexes)
                item = Item(value, projection, distance)
                if key not in self.items:
                    self.items[key] = [item]
                else:
                    self.items[key].append(item)           

        # for key in list(shapes_inside.keys()):
        #     for item in shapes_inside[key].v:
        #         vertex, distance = self.tool.get_minimum_shape_distance_inside_polygon(item, self.vertexes)
        #         print(self.tool.get_shape_name_by_id(item.) vertex, distance)


        

class Floor():
    ID: int
    rooms: list[Room] = []

    def __init__(self, graph):
        self.graph = graph
        self.G = nx.Graph(graph)

        for room in nx.minimum_cycle_basis(self.G):
            self.rooms.append(Room(room, self))

    def add_vertex(self, vertex: tuple):
        # Нужно найти ребро, которое пренадлежит вершине.
        ...

# class Building():
#     floors: list[Floor]

#     def __init__(self, graph: dict):
#         # Пройтись по каждому уникальному
#         ...

