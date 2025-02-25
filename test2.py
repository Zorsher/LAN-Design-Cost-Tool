from vsdx import VisioFile, Connect

with VisioFile('test.vsdx') as visio:
    for page in visio.pages:
        for shape in page.child_shapes:
            print(f"Фигура {shape.ID}: {shape.text}")
            if shape.connects:
                for conn in shape.connects:
                    conn: Connect
                    print(f"  → Соединение с {conn.to_id}")
