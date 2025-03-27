import math
import networkx as nx
import matplotlib.pyplot as plt
import win32com.client
import os

from utils.TempFile import TempFilesManager
from vsdx import VisioFile as VsdxFile
from vsdx import Shape, Page
from networkx import Graph

ROUND = 2

class VisioTool():
    """
    Класс для работы с файлом Visio
    """
    _isinstance = None
    _shapes_loaded = False
    master_shapes: dict

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

        self.master_shapes = {}
        self._shapes_loaded = True
        for shape in self.file.master_index.values():
            # print(shape.page_id, "ya tut")
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
        for key, value in self.file.master_index.items():
            if int(value.page_id) == int(id):
                return key

    def get_shapes_intersection(self, first_shape: Shape, second_shape: Shape):
        """
        Возвращает пересечение между фигурами. `None`, если пересечений нет
        """
        f_x1, f_y1, f_x2, f_y2 = (round(bound, ROUND) for bound in first_shape.bounds)
        s_x1, s_y1, s_x2, s_y2 = (round(bound, ROUND) for bound in second_shape.bounds)

        f_x1, f_y1, f_x2, f_y2 = (min(f_x1, f_x2), min(f_y1, f_y2), max(f_x1, f_x2), max(f_y1, f_y2))
        s_x1, s_y1, s_x2, s_y2 = (min(s_x1, s_x2), min(s_y1, s_y2), max(s_x1, s_x2), max(s_y1, s_y2))

        if f_x1 == f_x2 and s_x1 <= f_x1 <= s_x2:
            if (f_y1 <= s_y1 <= f_y2):
                return (f_x1, s_y1), (s_x2, s_y2)
                
            elif (f_y1 <= s_y2 <= f_y2):
                return (f_x1, s_y2), (s_x1, s_y1)

        elif f_y1 == f_y2 and s_y1 <= f_y1 <= s_y2:
            if (f_x1 <= s_x1 <= f_x2):
                return (s_x1, f_y1), (s_x2, s_y2)

            elif (f_x1 <= s_x2 <= f_x2):
                return (s_x2, f_y2), (s_x1, s_y1)
   
    def get_shapes_connections(self, shapes: list[Shape]):
        """
        Получить все связи между фигурами
        """
        connects = {}
        for shape in shapes:
            _x1, _y1, _x2, _y2 = shape.bounds
            bounds = ((min(_x1, _x2), min(_y1, _y2), max(_x1, _x2), max(_y1, _y2)))
            x1, y1, x2, y2 = (round(bound, ROUND) for bound in bounds)

            dist = round(math.dist([x1, y1], [x2, y2]), ROUND)
            
            if (x1, y1) not in connects:
                connects[(x1, y1)] = {(x2, y2): dist}
            else:
                connects[(x1, y1)][(x2, y2)] = dist

            if (x2, y2) not in connects:
                connects[(x2, y2)] = {(x1, y1): dist}
            else:
                connects[(x2, y2)][(x1, y1)] = dist

            intersections = [(x2, y2), (x1, y1)]

            for checked_shape in shapes:
                if shape.ID == checked_shape.ID:
                    continue

                data = self.get_shapes_intersection(shape, checked_shape)

                if data is None:
                    continue

                new_node, opposite_node = data

                intersections.sort()

                for i in range(len(intersections) - 1):
                    previous_node = intersections[i]
                    next_node = intersections[i+1]

                    # Если новая точка равна по x или y с предыдущей или следующей точкой, но при этом она находится вне них
                    if ((previous_node[0] == next_node[0] == new_node[0] and (new_node[1] < previous_node[1] or new_node[1] > next_node[1])) or
                        (previous_node[1] == next_node[1] == new_node[1] and (new_node[0] < previous_node[0] or new_node[0] > next_node[0]))
                        ):
                        continue
                    # Если точка не равна ни по x, ни по y с предыдущей или следующей точкой
                    elif previous_node[0] != next_node[0] and previous_node[1] != next_node[1]:
                        t_x = (new_node[0] - previous_node[0]) / (next_node[0] - previous_node[0])                        
                        t_y = (new_node[1] - previous_node[1]) / (next_node[1] - previous_node[1])

                        # Тогда вычисляем коэффииент t и проверяем, что он не входит в диапазон 0>=t<=1
                        if t_x != t_y or (0 > t_x or 1 < t_x):
                            continue

                    if previous_node == new_node or new_node == next_node:
                        continue

                    connects[previous_node].pop(next_node)
                    connects[next_node].pop(previous_node)

                    previous_new_dist = round(math.dist(previous_node, new_node), ROUND)
                    next_new_dist = round(math.dist(next_node, new_node), ROUND)

                    connects[previous_node].update({new_node: previous_new_dist})
                    connects[next_node].update({new_node: next_new_dist})

                    if new_node not in list(connects.keys()):
                        connects[new_node] = {previous_node: previous_new_dist, next_node: next_new_dist}
                    else:
                        connects[new_node].update({previous_node: previous_new_dist, next_node: next_new_dist})

                    break

                if new_node not in intersections:
                    intersections.append(new_node)
                    intersections.sort()

        # jsonOperations.jsonDump("test", connects)

        return connects
    

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

            t = ((a_x * b_x) + (a_y * b_y)) / ((a_x ** 2) + (a_y ** 2))

            if 0 > round(t, ROUND) or 1 < round(t, ROUND):
                continue

            node = (p_x + t * a_x, p_y + t * a_y)

            distance = round(math.dist((x, y), node), ROUND)
            # print(previous_node, node, next_node, distance)
            distances.append(((round(node[0], ROUND), round(node[1], ROUND)), previous_node, next_node, distance))


        if len(distances) == 0:
            return
        
        distances.sort(key=lambda items: items[-1])

        return distances[0]
        
    def get_shapes_inside_polygon(self, polygon_node: list[tuple] | Graph, page: int = 0) -> dict[str, list[Shape]]:
        """
        Определяет все фигуры внутри многоугольника
        """
        shapes = {}
        all_shapes = self.file.pages[page].child_shapes

        if isinstance(polygon_node, Graph):
            polygon_node = list(nx.minimum_cycle_basis(polygon_node))[0]
            # print(polygon_node)

        for shape in all_shapes:
            # добавить whitelist для фигур, которые нужно учитывать
            if shape.master_page_ID == self.file.master_index["Wall"].page_id:
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

                x_intersection = previous_node[0] + (y - previous_node[1]) * ((next_node[0] - previous_node[0]) / (next_node[1] - previous_node[1]))
                
                if x_intersection > x:
                    intersections+=1

            if intersections == 0 or intersections % 2 == 0:
                continue

            if shape.master_page_ID not in shapes:
                shapes[shape.master_page_ID] = [shape]
            else:
                shapes[shape.master_page_ID].append(shape)
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
                    G.add_edge(node, neighbor, weight=round(weight))
            edges = list(G.edges)
        elif isinstance(graph, Graph):
            edges = list(graph.edges)

        for edge in edges:
            previous_node, next_node = edge

            # no way
            if (min(previous_node[0], next_node[0]) <= node[0] <= max(previous_node[0], next_node[0]) 
                and min(previous_node[1], next_node[1]) <= node[1] <= max(previous_node[1], next_node[1])
            ):
                return edge

            # if (
            #     (previous_node[0] == next_node[0] == node[0] and min(previous_node[1], next_node[1]) <= node[1] <= max(previous_node[1], next_node[1])) or
            #     (previous_node[1] == next_node[1] == node[1] and min(previous_node[0], next_node[0]) <= node[0] <= max(previous_node[0], next_node[0]))
            # ):
            #     return edge

            # if previous_node[0] != next_node[0] and previous_node[1] != next_node[1]:
            #     # Находим параметр t для x и y
            #     t_x = (node[0] - previous_node[0]) / (next_node[0] - previous_node[0])                        
            #     t_y = (node[1] - previous_node[1]) / (next_node[1] - previous_node[1])

            #     if round(t_x, 1) == round(t_y, 1) and 0 <= t_x <= 1:
            #         return edge

            

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
        next_node = end_node
        visited = [next_node]
        paths = [(next_node, 0)]

        for i in range(len(start_nodes)):
            nearest_nodees = [(node, nx.dijkstra_path_length(graph, node, next_node)) for node in start_nodes if node not in visited]
            nearest_nodees.sort(key = lambda items: items[-1])

            nearest_node, nearest_leight = nearest_nodees[0]
            end_leight = nx.dijkstra_path_length(graph, nearest_node, end_node)

            if nearest_leight <= end_leight:
                global_leight+= nearest_leight
                leight = nearest_leight+paths[i][-1]
            else:
                global_leight+= end_leight
                leight = end_leight

            visited.append(nearest_node)
            paths.append((nearest_node, leight))
            next_node = nearest_node

        return paths, global_leight
    
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



