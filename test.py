def find_corner_connections(bounds):
    walls = []
    for bound in bounds:
        x1, y1, x2, y2 = bound
        walls.append(((x1, y1), (x2, y2)))  # Храним стены как пары точек

    connections = {}
    
    for i, (start1, end1) in enumerate(walls):
        for j, (start2, end2) in enumerate(walls):
            if i == j:
                continue  # Не сравниваем стену саму с собой
            
            # Проверяем, есть ли у стен общая точка (угловое соединение)
            if start1 == start2 or start1 == end2 or end1 == start2 or end1 == end2:
                if i not in connections:
                    connections[i] = []
                connections[i].append(j)

    return connections

bounds = [
(1.574803099347564, 2.300688902953082, 1.574803099347564, 10.18700754890456),
(1.574803099347564, 2.300688902953082, 6.692913172227147, 2.300688902953082),
(6.692913172227147, 2.300688902953082, 6.692913172227146, 10.18700754890454),
(1.574803099347564, 10.18700754890456, 6.692913172227146, 10.18700754890454)
]

corner_connections = find_corner_connections(bounds)
print(corner_connections)
