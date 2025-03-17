from visio import VisioTool
from classes import Floor
from vsdx import Page, Shape

def main():
    visioFile = VisioTool("files/domru.vsdx")
    print(visioFile.file.master_index.keys())

    # visioFile.page_connections()
    shapes = visioFile.get_shapes_by_name("Wall")
    graph = visioFile.get_shapes_connections(shapes)

    fl = Floor(graph)

    # print(fl.rooms[0].items)

    # dfs_stack(graph, "1.0:2.0")


if __name__ == "__main__":
    main()