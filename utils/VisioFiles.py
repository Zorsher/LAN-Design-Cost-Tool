import math
import networkx as nx
import matplotlib.pyplot as plt
import win32com.client
import os

from utils.TempFile import TempFilesManager
from vsdx import VisioFile as VsdxFile
from vsdx import Shape, Page, Connect
from networkx import Graph

ROUND = 2
INCH_TO_M = 0.0254
EPS = 1e-8 

class VisioTool():
    """
    Класс для работы с файлом Visio
    """
    _isinstance = None
    _shapes_loaded = False
    master_shapes: dict[int, tuple[Page, str]]

    def __new__(cls, file_path: str = None):
        if cls._isinstance is None:

            with VsdxFile(file_path) as file:
                cls.file = file

            cls.visio = win32com.client.Dispatch("Visio.Application")
            cls.visio.Visible = False
            cls.com_file = cls.visio.Documents.Open(file_path)

            cls._isinstance = super().__new__(cls)

        return cls._isinstance
    
    def __del__(self):
        self.com_file.Close()
        self.visio.Quit()

    def __init__(self, file_path = None):
        if self._shapes_loaded:
            return

        self._shapes_loaded = True
        self.master_shapes = {}
        items = self.com_file.Masters.GetNames()

        existing_items = set()

        # как это ускорить?
        for page in self.com_file.Pages:
            for shape in page.Shapes:
                try:
                    master_id = shape.Master.ID
                except:
                    continue

                existing_items.add(master_id) if master_id not in existing_items else None


        # произошла локализация
        for shape, com_shape in zip(self.file.master_pages, items):
            if int(shape.page_id) not in existing_items:
                continue

            name = str(com_shape)

            try:
                name = name.split(".")[0]
            except:
                ...

            shape.name = name # Я ИЗМЕНИЛ ОСНОВНУЮ БИБЛИОТЕКУ АЛЯРМ!
            path = self.save_shape_in_new_file(shape.page_id)
            self.master_shapes[shape.page_id] = (shape, path)

    def get_shape_id_by_name(self, shape_name: str):
        """
        Получить ID фигуры по её названию
        """
        try:
            return self.file.master_index[shape_name].page_id
        except:
            return None

    def get_shapes_by_id(self, id: int, page: int = 0):
        """
        Получить все фигуры по ID мастера и номеру страницы
        """
        shapes = [shape for shape in self.file.pages[page].child_shapes if id == shape.master_page_ID]
        return shapes
    
    def get_shapes_by_name(self, shape_name: str, page: int = 0):
        """
        Получить все фигуры по имени мастера и номеру страницы
        """
        if shape_name not in list(self.file.master_index.keys()):
            return []
        
        master_id = self.get_shape_id_by_name(shape_name)
        shapes = self.get_shapes_by_id(master_id, page)
        return shapes
    
    def get_shape_name_by_id(self, id: int) -> str:
        """
        Получить имя фигуры по ID
        """
        try:
            for key, value in self.file.master_index.items():
                if int(value.page_id) == int(id):
                    return key
        except Exception as e:
            ...

    def get_shapes_connections(self, shapes: list[Shape]):
        """
        Получить все связи между фигурами
        """
        graph = nx.Graph()
        for shape in shapes:
            _x1, _y1, _x2, _y2 = shape.bounds
            x1, y1, x2, y2 = (round(bound, ROUND) for bound in shape.bounds)

            dist = math.dist([_x1, _y1], [_x2, _y2]) * INCH_TO_M
            
            graph.add_edge((x1, y1), (x2, y2), weight=dist)

            nodes = [(x2, y2), (x1, y1)]

            for connected_shape in shapes:
                if connected_shape.ID == shape.ID:
                    continue
            
                x3, y3, x4, y4 = (round(bound, ROUND) for bound in connected_shape.bounds)

                A = x2 - x1
                B = -(x4 - x3)
                C = y2 - y1
                D = -(y4 - y3)
                E = x3 - x1
                F = y3 - y1

                delta = A*D - B*C
                delta_t = E*D - B*F
                delta_u = A*F - E*C

                if abs(delta) <= EPS:
                    continue
                
                t = delta_t / delta
                u = delta_u / delta

                if not (0 - EPS <= t <= 1 + EPS and 0 - EPS <= u <= 1 + EPS):
                    continue

                xi = x1 + t*(x2 - x1)
                yi = y1 + t*(y2 - y1)
                _new_node = (xi, yi)

                # а зачем мне так много условий в предыдущем коде, если я могу добавить новую ноду в список, отсортировать его и взять предыдущую и следующую ноду? 
                new_node = (round(_new_node[0], ROUND), round(_new_node[1], ROUND))

                if new_node in nodes:
                    continue

                nodes.append(new_node)
                nodes.sort(key=lambda items: (items[0]**2) + (items[1]**2))

                previous_node = nodes[nodes.index(new_node)-1]
                next_node = nodes[nodes.index(new_node)+1]

                graph.remove_edge(previous_node, next_node)
                
                previous_new_dist = math.dist(previous_node, _new_node) * INCH_TO_M
                new_next_dist = math.dist(_new_node, next_node) * INCH_TO_M

                graph.add_edge(previous_node, new_node, weight=previous_new_dist)
                graph.add_edge(new_node, next_node, weight=new_next_dist)

                # print(previous_node, new_node, next_node, nodes)

        nodes = graph.copy().nodes

        for node in nodes:
            len_neighbors = len([n for n in graph.neighbors(node)])
            if len_neighbors <= 1:
                graph.remove_node(node)

        return graph


    def get_minimum_shape_distance_inside_polygon(self, shape: Shape, polygon_node: list[tuple] | Graph, page: int = 0) -> list:
        """
        Определяет минимальное расстояние от фигуры до многоугольника
        """
        x, y = shape.center_x_y
        distances = []

        if isinstance(polygon_node, Graph):
            polygon_node = list(nx.minimum_cycle_basis(polygon_node))[0]

        for i in range(len(polygon_node)):
            previous_node = polygon_node[i-1]
            next_node = polygon_node[i]

            p_x, p_y = previous_node
            n_x, n_y = next_node
            
            a_x, a_y = n_x - p_x, n_y - p_y
            b_x, b_y = x - p_x, y - p_y

            try:
                t = ((a_x * b_x) + (a_y * b_y)) / ((a_x ** 2) + (a_y ** 2))
            except Exception as e:
                t = 0

            if 0 > round(t, ROUND) or 1 < round(t, ROUND):
                continue

            node = (p_x + t * a_x, p_y + t * a_y)

            distance = math.dist((x, y), node)*INCH_TO_M
            distances.append(((round(node[0], ROUND), round(node[1], ROUND)), previous_node, next_node, distance))


        if len(distances) == 0:
            return
        
        distances.sort(key=lambda items: items[-1])

        return distances[0]
        
    def get_shapes_inside_polygon(self, wall_shape: Page, polygon_node: list[tuple] | Graph, page: int = 0) -> dict[str, list[Shape]]:
        """
        Определяет все фигуры внутри многоугольника
        """
        shapes = {}
        all_shapes = self.file.pages[page].child_shapes

        if isinstance(polygon_node, Graph):
            polygon_node = list(nx.minimum_cycle_basis(polygon_node))[0]

        for shape in all_shapes:
            # добавить whitelist для фигур, которые нужно учитывать
            if shape.master_page_ID == wall_shape.page_id:
                continue

            x, y = shape.center_x_y
            intersections = 0
            # Если количество пересечений луча с многоугольником чётное - фигура снаружи многоугольника, иначе - внутри
            for i in range(len(polygon_node)):
                previous_node = polygon_node[i-1]
                next_node = polygon_node[i]

                if previous_node[1] == next_node[1]:
                    continue

                if y < min(previous_node[1], next_node[1]) or y > max(previous_node[1], next_node[1]):
                    continue

                if x > max(previous_node[0], next_node[0]):
                    continue

                # x_intersection = previous_node[0] + (y - previous_node[1]) * ((next_node[0] - previous_node[0]) / (next_node[1] - previous_node[1]))
                x_intersection = previous_node[0] + (next_node[0] - previous_node[0]) * ((y - previous_node[1]) / (next_node[1] - previous_node[1]))
                
                if x_intersection > x:
                    intersections+=1

            if intersections == 0 or intersections % 2 == 0:
                continue

            shapes.setdefault(shape.master_page_ID, []).append(shape)
        return shapes

    def find_edge_for_node(self, node: tuple, graph: dict | Graph) -> tuple:
        """
        Находит ребро, которое пренадлежит вершине
        """

        # Проходится по каждому циклу и при нахождении точки прерываться?
        if isinstance(graph, dict):
            # Есть бескомпромиссный вариант переделать словарь в Graph
            G = nx.Graph()
            for node, neighbors in graph.items():
                for neighbor, weight in neighbors.items():
                    G.add_edge(node, neighbor, weight=weight)
            edges = list(G.edges)
        elif isinstance(graph, Graph):
            edges = list(graph.edges)

        for edge in edges:
            previous_node, next_node = edge

            if (min(previous_node[0], next_node[0]) <= node[0] <= max(previous_node[0], next_node[0]) 
                and min(previous_node[1], next_node[1]) <= node[1] <= max(previous_node[1], next_node[1])
            ):
                return edge

    def save_graph(self, name,  graph: Graph, colors: list = "black", debug: bool = False) -> str: # так называемый дебаг
        tmp = TempFilesManager()

        poses = {}
        edge_labels = ""

        for key in graph.nodes:
            # print(key)
            x, y = key[0], key[1]
            poses[key] = (float(x), float(y))

        if debug:
            nx.draw_networkx_nodes(graph, poses, node_size=500, node_color="lightblue")
            nx.draw_networkx_labels(graph, poses, font_size=8)
            edge_labels = nx.get_edge_attributes(graph, "weight")


        nx.draw_networkx_edges(graph, poses, edge_color=colors, width=2)
        nx.draw_networkx_edge_labels(graph, poses, edge_labels=edge_labels, font_size=7)
        plt.axis("off")
        # plt.show()

        path = tmp._tempDir.path() + "\\" + name + ".png"
        plt.savefig(fname = path)

        return path
    
    def find_minimum_paths_in_graph(self, graph: Graph, start_nodes, end_node):
        """
        Находит единый путь в заданном графе от начальных вершин до конечной вершины
        """
        
        global_leight = 0
        previous_node = end_node
        visited = [previous_node]
        paths = [[previous_node, 0]]

        for i in range(len(start_nodes)):
            nearest_nodees = [[node, nx.dijkstra_path_length(graph, node, previous_node)] for node in start_nodes if node not in visited]
            nearest_nodees.sort(key = lambda items: items[-1])

            if len(nearest_nodees) == 0:
                break

            nearest_node, nearest_leight = nearest_nodees[0]
            end_leight = nx.dijkstra_path_length(graph, nearest_node, end_node)

            if nearest_leight <= end_leight:
                global_leight+= nearest_leight
                leight = nearest_leight+paths[i][-1]
            else:
                global_leight+= end_leight
                leight = end_leight

            visited.append(nearest_node)
            paths.append([nearest_node, leight])
            previous_node = nearest_node

        return paths, global_leight
    
    def get_minimum_distance_to_graph_nodes(self, graph: Graph, start_node: tuple, graph_nodes: list):
        edge = self.find_edge_for_node(start_node, graph)

        min_edge_nodes_paths = []

        for node in edge:
            path = math.dist(start_node, node) * INCH_TO_M

            min_path_to_graph_node = [[graph_node, nx.dijkstra_path_length(graph, node, graph_node)] for graph_node in graph_nodes if graph_node in graph.nodes]
            min_path_to_graph_node.sort(key = lambda items: items[-1])

            nearest_node, nearest_leight = min_path_to_graph_node[0]
            min_edge_nodes_paths.append((nearest_node, path+nearest_leight))

        min_edge_nodes_paths.sort(key = lambda items: items[-1])

        return min_edge_nodes_paths[0]


    
    def draw_graph(self, graph: Graph, colors: list = "black", debug: bool = False) -> str: # так называемый дебаг
        tmp = TempFilesManager()

        poses = {}
        edge_labels = ""

        for key in graph.nodes:
            # print(key)
            x, y = key[0], key[1]
            poses[key] = (float(x), float(y))

        if debug:
            nx.draw_networkx_nodes(graph, poses, node_size=500, node_color="lightblue")
            nx.draw_networkx_labels(graph, poses, font_size=8)
            edge_labels = nx.get_edge_attributes(graph, "weight")


        nx.draw_networkx_edges(graph, poses, edge_color=colors, width=2)
        nx.draw_networkx_edge_labels(graph, poses, edge_labels=edge_labels, font_size=7)
        plt.axis("off")
        plt.show()

    def save_graph_with_highlighted_edges(self, name, graph: Graph, edges: list[tuple], color: str = "red") -> str:
        edge_colors = ["red" if edge in edges else "black" for edge in graph.edges]
        path = self.save_graph(name, graph, edge_colors)
        return path
    
    def draw_graph_with_highlighted_edges(self, graph: Graph, edges: list[tuple], color: str = "red") -> str:
        edge_colors = ["red" if edge in edges else "black" for edge in graph.edges]
        path = self.draw_graph(graph, edge_colors)
        return path


    def save_shape_in_new_file(self, shape: Shape | int):
        tmp = TempFilesManager()
        ID = shape.master_page_ID if isinstance(shape, Shape) else shape
        shape = self.com_file.Masters.ItemFromID(ID)
        path = tmp._tempDir.path() + "\\" + f"{ID}.png"
        shape.Export(path)
        return path



