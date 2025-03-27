# import win32com.client 


# input_file = "C:\\Users\\zorsher\\Desktop\\дипло\\files\\domru.vsdx"
# output_file = "C:\\Users\\zorsher\\Desktop\\дипло\\"
# shape_id = 1215  # ID нужной фигуры

# # Открываем Visio
# visio = win32com.client.Dispatch("Visio.Application")
# visio.Visible = False

# doc = visio.Documents.Open(input_file)
# print(dir(doc.Pages))

# # sh = doc.Masters.ItemFromID(13)
# # # for master in doc.Masters:
# # #     if master.ID == 12:
# # #         print(master)

# # # sh = page.Shapes.ItemFromID(shape_id)
# # sh.Export(output_file + "output.png")

# # doc.Close()
# # visio.Quit()


print(1%2)