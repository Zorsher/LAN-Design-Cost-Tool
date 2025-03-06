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
            
            if f"{x1}:{y1}" not in connects:
                connects[f"{x1}:{y1}"] = {f"{x2}:{y2}": bounds[2] - bounds[0] if y1 == y2 else bounds[3] - bounds[1]}
            else:
                connects[f"{x1}:{y1}"][f"{x2}:{y2}"] = bounds[2] - bounds[0] if y1 == y2 else bounds[3] - bounds[1]

            if f"{x2}:{y2}" not in connects:
                connects[f"{x2}:{y2}"] = {f"{x1}:{y1}": bounds[2] - bounds[0] if y1 == y2 else bounds[3] - bounds[1]}
            else:
                connects[f"{x2}:{y2}"][f"{x1}:{y1}"] = bounds[2] - bounds[0] if y1 == y2 else bounds[3] - bounds[1]

            intersections = [(x2, y2), (x1, y1)]

            for checked_shape in shapes:
                if shape.ID == checked_shape.ID:
                    continue

                data = self.get_shapes_intersection(shape, checked_shape)

                if data is None:
                    continue

                # print(shape.ID, checked_shape.ID, intersections, data)

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

                    # print(shape.ID, checked_shape.ID, previous_coords, new_coords, next_coords, new_coords == previous_coords, new_coords == next_coords)
                    # if shape.ID == str(1):
                    #     print(checked_shape.ID, previous_coords, new_coords, next_coords)

                    if previous_coords == new_coords or new_coords == next_coords:
                        if opposite_coords == new_coords:
                            continue

                        distance = math.dist(opposite_coords, new_coords)
                        print(shape.ID, checked_shape.ID, opposite_coords, new_coords, distance)
                        if opposite_coords_name not in list(connects.keys()):
                            connects[opposite_coords_name] = {new_coords_name: distance}
                        else:
                            connects[opposite_coords_name][new_coords_name] = distance

                        if new_coords_name not in list(connects.keys()):
                            connects[new_coords_name] = {opposite_coords_name: distance}
                        else:
                            connects[new_coords_name][opposite_coords_name] = distance
                        break

                    try:
                        connects[previous_coords_name].pop(next_coords_name)

                    except Exception as e:
                        print("previous err", shape.ID, checked_shape.ID, previous_coords_name, next_coords_name, connects)
                        raise e
                    
                    try:
                        connects[next_coords_name].pop(previous_coords_name)
                    except Exception as e:
                        print("next err", shape.ID, checked_shape.ID, next_coords_name, previous_coords_name, connects)
                        raise e

                    previous_new_dist = math.dist(previous_coords, new_coords)
                    next_new_dist = math.dist(next_coords, new_coords)

                    connects[previous_coords_name].update({new_coords_name: previous_new_dist})
                    connects[next_coords_name].update({new_coords_name: next_new_dist})

                    if new_coords_name not in list(connects.keys()):
                        connects[new_coords_name] = {previous_coords_name: previous_new_dist, next_coords_name: next_new_dist}
                    else:
                        connects[new_coords_name].update({previous_coords_name: previous_new_dist, next_coords_name: next_new_dist})

                    break

                intersections.append(new_coords)
                intersections.sort()

        jsonOperations.jsonDump("test", connects)


















                
                # for i in range(len(intersections) - 1):
                #     previous_coords = intersections[i]
                #     next_coords = intersections[i+1]
                #     print(shape.ID, checked_shape.ID)
                #     if previous_coords[0] == next_coords[0] and new_coords["x"] == previous_coords[0]:
                #         print("X:")
                #         print(previous_coords[0], new_coords["x"], next_coords[0])
                #         print(previous_coords[1], new_coords["y"], next_coords[1])
                #         # if previous_coords[1] > new_coords["y"] < next_coords[1]:
                #         #     previous_point = f"{previous_coords[0]}:{previous_coords[1]}"
                #         #     next_point = f"{next_coords[0]}:{next_coords[1]}"
                #         #     new_point = f"{new_coords['x']}:{new_coords['y']}"

                #     elif previous_coords[1] == next_coords[1] and new_coords["y"] == previous_coords[1]:
                #         print("Y")
                #         print(previous_coords[0], new_coords["x"], next_coords[0])
                #         print(previous_coords[1], new_coords["y"], next_coords[1])
                #         # if previous_coords[0] > new_coords["x"] < next_coords[0]:
                #         #     previous_point = f"{previous_coords[0]}:{previous_coords[1]}"
                #         #     next_point = f"{next_coords[0]}:{next_coords[1]}"
                #         #     new_point = f"{new_coords['x']}:{new_coords['y']}"

                #     if previous_point is None:
                #         continue

                #     # intersections.append(tuple(new_point.split(":")))
                #     # connects[previous_point]["connections"].pop(next_point)

                #     intersections.sort()

                #     previous_point = None
                #     next_point = None
                #     new_point = None

                # print(intersections)
                    # t_x = (new_coords["x"] - previous_coords[0]) / (next_coords[0] - previous_coords[0])
                    # t_y = (new_coords["y"] - previous_coords[1]) / (next_coords[1] - previous_coords[1])
                    # print(t_x, t_y)
                    # print(f"t_x = (x_3 ({new_coords["x"]}) - x_1 ({previous_coords[0]})) / (x_2 ({next_coords[0]}) - x_1 ({previous_coords[0]}))")
                    # print(f"t_y = (y_3 ({new_coords["y"]}) - y_1 ({previous_coords[1]})) / (y_2 ({next_coords[1]}) - y_1 ({previous_coords[1]}))")


 




            # for connect in shape.connects:
            #     connect: Connect


            #     from_shape = self.file.pages[0].find_shape_by_id(connect.from_id)
            #     to_shape = self.file.pages[0].find_shape_by_id(connect.to_id)

            #     from_key = (from_shape.ID, from_shape.bounds)
            #     to_key = (to_shape.ID, to_shape.bounds)

            #     if shape.ID in list(connects.keys()):
            #         connects[(shape.ID)].append(connect.to_id if connect.from_id == shape.ID else connect.from_id)
            #     else:
            #         connects[shape.ID] = [connect.to_id if connect.from_id == shape.ID else connect.from_id]




            


            # Не трогать !!
            # for connect in shape.connects:
            #     connect: Connect
            #     if shape.ID in list(connects.keys()):
            #         # connects[shape.ID]["connects"].append(connect.connector_shape_id)
            #         connects[shape.ID].append(connect.connector_shape_id)
            #     else:
            #         connects[shape.ID] = [connect.connector_shape_id]
            #         # connects[shape.ID] = {"shape": shape, "connects": [connect.connector_shape_id]}

        return connects

    def page_connections(self, page: int = 0):
        connects = {}
        for connection in self.file.pages[page].connects:
            print(connection.from_id, connection.to_id)
            # print(connection.connector_shape_id, connection.from_id)
            # if connection.from_shape_id in list(connects.keys()):
            #     connects[connection.from_shape_id].append(connection.to_shape_id)
            # else:
            #     connects[connection.from_shape_id] = [connection.to_shape_id]

        return connects
