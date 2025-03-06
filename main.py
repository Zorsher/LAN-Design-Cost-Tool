from visio import VisioFile
from vsdx import Page, Shape

# Константы для преобразования
INCH_TO_CM = 2.54


def main():
    visioFile = VisioFile("files/domru.vsdx")

    # visioFile.page_connections()
    shapes = visioFile.get_shapes_by_name("Wall")
    connects = visioFile.get_shapes_connections(shapes)
    # print(connects)

if __name__ == "__main__":
    main()