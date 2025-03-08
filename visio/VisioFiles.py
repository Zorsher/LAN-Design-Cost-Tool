import math
from vsdx import VisioFile as VsdxFile, Shape, Page, Connect
from jsonOperations import jsonOperations

class VisioFile():
    """
    Класс для работы с файлом Visio
    """
    _isinstance = None

    def __new__(cls, file_path: str):
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

    # Переписать под формулу прямой y = kx + b
    def get_shapes_intersection(self, first_shape: Shape, second_shape: Shape):
        f_x1, f_y1, f_x2, f_y2 = (round(bound, 1) for bound in first_shape.bounds)
        s_x1, s_y1, s_x2, s_y2 = (round(bound, 1) for bound in second_shape.bounds)

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
            x1, y1, x2, y2 = (round(bound, 1) for bound in bounds)

            dist = math.dist([x1, y1], [x2, y2])
            
            if f"{x1}:{y1}" not in connects:
                connects[f"{x1}:{y1}"] = {f"{x2}:{y2}": dist}
            else:
                connects[f"{x1}:{y1}"][f"{x2}:{y2}"] = dist

            if f"{x2}:{y2}" not in connects:
                connects[f"{x2}:{y2}"] = {f"{x1}:{y1}": dist}
            else:
                connects[f"{x2}:{y2}"][f"{x1}:{y1}"] = dist

            intersections = [(x2, y2), (x1, y1)]

            for checked_shape in shapes:
                if shape.ID == checked_shape.ID:
                    continue

                data = self.get_shapes_intersection(shape, checked_shape)

                if data is None:
                    continue

                new_coords, opposite_coords = data

                new_coords_name = f"{new_coords[0]}:{new_coords[1]}"
                opposite_coords_name = f"{opposite_coords[0]}:{opposite_coords[1]}"

                intersections.sort()

                for i in range(len(intersections) - 1):
                    previous_coords = intersections[i]
                    next_coords = intersections[i+1]

                    previous_coords_name = f"{previous_coords[0]}:{previous_coords[1]}"
                    next_coords_name = f"{next_coords[0]}:{next_coords[1]}"

                    if previous_coords[0] == next_coords[0] == new_coords[0] and (new_coords[1] < previous_coords[1] or new_coords[1] > next_coords[1]):
                        continue

                    elif previous_coords[1] == next_coords[1] == new_coords[1] and (new_coords[0] < previous_coords[0] or new_coords[0] > next_coords[0]):
                        continue

                    elif previous_coords[0] != next_coords[0] and previous_coords[1] != next_coords[1]:
                        t_x = (new_coords[0] - previous_coords[0]) / (next_coords[0] - previous_coords[0])                        
                        t_y = (new_coords[1] - previous_coords[1]) / (next_coords[1] - previous_coords[1])

                        if t_x != t_y or (0 > t_x or 1 < t_x):
                            continue

                    if previous_coords == new_coords or new_coords == next_coords:
                        continue

                    connects[previous_coords_name].pop(next_coords_name)
                    connects[next_coords_name].pop(previous_coords_name)

                    previous_new_dist = math.dist(previous_coords, new_coords)
                    next_new_dist = math.dist(next_coords, new_coords)

                    connects[previous_coords_name].update({new_coords_name: previous_new_dist})
                    connects[next_coords_name].update({new_coords_name: next_new_dist})

                    if new_coords_name not in list(connects.keys()):
                        connects[new_coords_name] = {previous_coords_name: previous_new_dist, next_coords_name: next_new_dist}
                    else:
                        connects[new_coords_name].update({previous_coords_name: previous_new_dist, next_coords_name: next_new_dist})

                    break

                if new_coords not in intersections:
                    intersections.append(new_coords)
                    intersections.sort()

        jsonOperations.jsonDump("test", connects)

        return connects

