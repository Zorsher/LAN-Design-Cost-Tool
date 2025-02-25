from vsdx import VisioFile as VsdxFile, Shape, Page, Connect


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
        shapes = [shape for shape in self.file.pages[page].child_shapes if id == shape.master_page_ID]
        return shapes
    
    def get_shapes_by_name(self, shape_name: str, page: int = 0):
        if shape_name not in list(self.file.master_index.keys()):
            return []
        
        master_id = self.file.master_index[shape_name].page_id
        shapes = self.get_shapes_by_id(master_id, page)
        return shapes
    
    def get_shapes_connections(self, shapes: list[Shape]):
        connects = {}
        to_recheck = {}
        for shape in shapes:
            if len(shape.connects) == 0 or len(shape.connects) <= 2:
                to_recheck[shape.ID] = shape

            for connect in shape.connects:
                connect: Connect
                if shape.ID in list(connects.keys()):
                    connects[shape.ID].append(connect.to_id if connect.from_id == shape.ID else connect.from_id)
                else:
                    connects[shape.ID] = [connect.to_id if connect.from_id == shape.ID else connect.from_id]



        for shapeID, shape in list(to_recheck.items()):
            


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
