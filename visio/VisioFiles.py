import math
from vsdx import VisioFile as VsdxFile, Shape, Page, Connect
from jsonOperations import jsonOperations
from networkx import Graph

ROUND = 5

class VisioTool():
    """
    Класс для работы с файлом Visio
    """
    _isinstance = None

    def __new__(cls, file_path: str = None):
        if cls._isinstance is None:

            with VsdxFile(file_path) as file:
                cls.file = file
            cls._isinstance = super().__new__(cls)

        return cls._isinstance
    
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
        
        master_id = self.file.master_index[shape_name].page_id
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

                new_vertex, opposite_vertex = data

                new_vertex_name = (new_vertex[0], new_vertex[1])
                opposite_vertex_name = (opposite_vertex[0], opposite_vertex[1])

                intersections.sort()

                for i in range(len(intersections) - 1):
                    previous_vertex = intersections[i]
                    next_vertex = intersections[i+1]

                    previous_vertex_name = (previous_vertex[0], previous_vertex[1])
                    next_vertex_name = (next_vertex[0], next_vertex[1])

                    # Если новая точка равна по x или y с предыдущей или следующей точкой, но при этом она находится вне них
                    if ((previous_vertex[0] == next_vertex[0] == new_vertex[0] and (new_vertex[1] < previous_vertex[1] or new_vertex[1] > next_vertex[1])) or
                        (previous_vertex[1] == next_vertex[1] == new_vertex[1] and (new_vertex[0] < previous_vertex[0] or new_vertex[0] > next_vertex[0]))
                        ):
                        continue
                    # Если точка не равна ни по x, ни по y с предыдущей или следующей точкой
                    elif previous_vertex[0] != next_vertex[0] and previous_vertex[1] != next_vertex[1]:
                        t_x = (new_vertex[0] - previous_vertex[0]) / (next_vertex[0] - previous_vertex[0])                        
                        t_y = (new_vertex[1] - previous_vertex[1]) / (next_vertex[1] - previous_vertex[1])

                        # Тогда вычисляем коэффииент t и проверяем, что он не входит в диапазон 0>=t<=1
                        if t_x != t_y or (0 > t_x or 1 < t_x):
                            continue

                    if previous_vertex == new_vertex or new_vertex == next_vertex:
                        continue

                    connects[previous_vertex_name].pop(next_vertex_name)
                    connects[next_vertex_name].pop(previous_vertex_name)

                    previous_new_dist = round(math.dist(previous_vertex, new_vertex), ROUND)
                    next_new_dist = round(math.dist(next_vertex, new_vertex), ROUND)

                    connects[previous_vertex_name].update({new_vertex_name: previous_new_dist})
                    connects[next_vertex_name].update({new_vertex_name: next_new_dist})

                    if new_vertex_name not in list(connects.keys()):
                        connects[new_vertex_name] = {previous_vertex_name: previous_new_dist, next_vertex_name: next_new_dist}
                    else:
                        connects[new_vertex_name].update({previous_vertex_name: previous_new_dist, next_vertex_name: next_new_dist})

                    break

                if new_vertex not in intersections:
                    intersections.append(new_vertex)
                    intersections.sort()

        # jsonOperations.jsonDump("test", connects)

        return connects

    def get_minimum_shape_distance_inside_polygon(self, shape: Shape, polygon_vertex: list[tuple], page: int = 0) -> dict:
        """
        Определяет минимальное расстояние от фигуры до многоугольника
        """
        x, y = shape.center_x_y
        distances = []

        for i in range(len(polygon_vertex) - 1):
            previous_vertex = polygon_vertex[i]
            next_vertex = polygon_vertex[i+1]
            
            # Если точка находится вне отрезка, то зачем её пропускать? 
            # if previous_vertex[0] == next_vertex[0] and (x < min(previous_vertex[0], next_vertex[0]) or x > max(previous_vertex[0], next_vertex[0])):
            #     continue
            # elif previous_vertex[1] == next_vertex[1] and (y < min(previous_vertex[1], next_vertex[1]) or y > max(previous_vertex[1], next_vertex[1])):
            #     continue

            if previous_vertex[0] == next_vertex[0]:
                vertex = (previous_vertex[0], y)
            elif previous_vertex[1] == next_vertex[1]:
                vertex = (x, previous_vertex[1])
            else:
                vertex = (
                    previous_vertex[0] + (y - previous_vertex[1]) * ((next_vertex[0] - previous_vertex[0]) / (next_vertex[1] - previous_vertex[1])),
                    previous_vertex[1] + (x - previous_vertex[0]) * ((next_vertex[1] - previous_vertex[1]) / (next_vertex[0] - previous_vertex[0]))
                    )

            distance = math.dist(shape.center_x_y, vertex)
            distances.append(((round(vertex[0], ROUND), round(vertex[1], ROUND)), distance))


        if len(distances) == 0:
            return
        
        distances.sort(key=lambda items: items[-1])

        return distances[0]
        
    def get_shapes_inside_polygon(self, polygon_vertex: list[tuple], page: int = 0) -> dict[str, list[Shape]]:
        """
        Определяет все фигуры внутри многоугольника
        """
        shapes = {}
        all_shapes = self.file.pages[page].child_shapes

        for shape in all_shapes:
            x, y = shape.center_x_y
            intersections = 0
            # Если количество пересечений луча с многоугольником чётное - фигура снаружи многоугольника, иначе - внутри
            for i in range(len(polygon_vertex) - 1):
                previous_vertex = polygon_vertex[i]
                next_vertex = polygon_vertex[i+1]

                if previous_vertex[1] == next_vertex[1]:
                    continue

                if y < min(previous_vertex[1], next_vertex[1]) or y > max(previous_vertex[1], next_vertex[1]):
                    continue

                if x > max(previous_vertex[0], next_vertex[0]):
                    continue

                x_intersection = previous_vertex[0] + (y - previous_vertex[1]) * ((next_vertex[0] - previous_vertex[0]) / (next_vertex[1] - previous_vertex[1]))
                
                if x_intersection > x:
                    intersections+=1

            if intersections == 0 or intersections % 2 == 0:
                continue

            if shape.master_page_ID not in shapes:
                shapes[shape.master_page_ID] = [shape]
            else:
                shapes[shape.master_page_ID].append(shape)
        return shapes

    def find_edge_for_vertex(self, vertex: tuple, graph: dict | Graph):
        """
        Находит ребро, которое пренадлежит вершине
        """
        if isinstance(graph, dict):
            # Есть бескромпромиссный вариант переделать словарь в Graph
            ...
        elif isinstance(graph, Graph):
            edges = graph.edges

        for edge in edges:
            previous_vertex, next_vertex = edge

            if previous_vertex[0] == next_vertex[0]:
                ...
            elif previous_vertex[1] == next_vertex[1]:
                ...
            else:
                ...





