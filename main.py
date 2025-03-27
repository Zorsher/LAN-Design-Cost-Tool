from utils import *
from classes import Floor
from vsdx import Page, Shape
from gui import MainWindow, Application

def main():
    import sys
    tmp = TempFilesManager()

    # visioFile = VisioTool("C:\\Users\\zorsher\\Desktop\\дипло\\files" + "\\" + "domru.vsdx")
    # # print(visioFile.file.master_index.keys())

    # # visioFile.page_connections()
    # shapes = visioFile.get_shapes_by_name("Wall")
    # graph = visioFile.get_shapes_connections(shapes)

    # fl = Floor(graph)
    # for room in fl.rooms:
    #     visioFile.draw_graph_with_highlighted_edges(fl.G, room.graph.edges)


    app = Application([])

    gui = MainWindow()
    gui.show()

    sys.exit(app.exec())



    # fl = gui.fl


if __name__ == "__main__":
    main()