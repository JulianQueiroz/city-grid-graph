import numpy as np
from operator import add
from itertools import combinations

def DFS(matrix, x, y, visited, target):
    if x < 0 or x >= matrix.shape[0] or y < 0 or y >= matrix.shape[1]:
        return

    if matrix[x, y] != target or (x, y) in visited:
        return

    visited.add((x, y))

    DFS(matrix, x - 1, y, visited, target)
    DFS(matrix, x + 1, y, visited, target)
    DFS(matrix, x, y + 1, visited, target)
    DFS(matrix, x, y - 1, visited, target)

def count_groups(matrix, look_for) -> list:
    """counts orthogonally connected elements as groups."""
    visited = set()
    all_groups = []
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i, j] == look_for and (i, j) not in visited:
                new_group = set()
                DFS(matrix, i, j, new_group, look_for)
                all_groups.append(new_group)
                visited.update(new_group)
    return all_groups

def update_groups_id(matrix, groups, node_type) -> set:
    """assigns unique IDs to groups or individual elements."""
    all_groups_id = set()
    for i, group in enumerate(groups, start=1):
        for position in group:
            group_id = f"{node_type}{i}"
            matrix[position] = group_id
            all_groups_id.add(group_id)
    return all_groups_id

def look_for_road_connection(matrix, groups, road_intersection_id) -> dict:
    """iterates over the position of each road group, checking its neighbors
    and identifying buildings/warehouses that the road connects to."""
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    road_connections = {}
    for group in groups:
        for position in group:
            connected_entities = set()
            for adjacent_position in directions:
                nx, ny = tuple(map(add, position, adjacent_position))
                if nx < 0 or nx >= matrix.shape[0] or ny < 0 or ny >= matrix.shape[1]:
                    continue
                if matrix[nx, ny].startswith("P") or matrix[nx, ny].startswith("A") or matrix[nx, ny].startswith(road_intersection_id):
                    connected_entities.add(matrix[nx, ny])
            road_connections.setdefault(matrix[position], set()).update(connected_entities)
    return road_connections

def lookup_road_connections_deadends_intersections(road_one_connections, road_two_connections) -> list:
    """categorizes connections through roads, intersections, and dead ends."""
    road_intersections, road_dead_ends, road_direct_connections = [], set(), {}
    # roads with width 1
    for road_id, road_connections in road_one_connections.items():
        build_connections = [build_id for build_id in road_connections if not build_id.startswith("E")]
        intersections = [rid for rid in road_connections if rid not in build_connections]
        # direct connections passing through only one road
        if len(build_connections) > 1:
            for combination in combinations(build_connections, 2):
                road_direct_connections.setdefault(road_id, set()).update([combination])
        else:  # dead-end road
            # road connects to only one building or warehouse
            if len(build_connections) == 1:
                road_dead_ends.add(f'{road_id}-{build_connections[0]}')
            else:
                road_dead_ends.add(road_id)
        # intersections passing through more than one road
        for rid in intersections:
            build_connections = [build_id for build_id in road_two_connections[rid] if not build_id.startswith("E")]
            if len(build_connections) > 1:
                road_intersections.append(f"{road_id}-{rid}")
            else:
                # road connects to only one building or warehouse
                if len(build_connections) == 1:
                    road_dead_ends.add(f'{rid}-{build_connections[0]}')
                else:
                    road_dead_ends.add(rid)

    road_connections = {}
    for road_ids in road_intersections:
        road_id_one, road_id_two = road_ids.split("-")
        if road_id_one.startswith("E1"):
            build_connections = [build_id for build_id in road_two_connections[road_id_two] if not build_id.startswith("E")]
            for combination in combinations(build_connections, 2):
                road_connections.setdefault(road_ids, set()).update([combination])
        else:
            build_connections = [build_id for build_id in road_one_connections[road_id_two] if not build_id.startswith("E")]
            for combination in combinations(build_connections, 2):
                road_connections.setdefault(road_ids, set()).update([combination])
    return road_connections, road_direct_connections, road_dead_ends

def build_graphviz_graph(building_ids, warehouse_ids, road_intersections, road_direct_connections, road_dead_ends):
    """generates a graph in Graphviz format."""
    with open("result.dot", "w", encoding="utf-8") as file:
        file.write("graph Result {\n")
        file.write("\tnode [shape=circle, style=filled, color=lightblue];\n")
        file.write("\tedge [color=gray];\n")
        # create nodes for buildings
        for build_id in building_ids:
            file.write(f'\t{build_id} [label="Building-{build_id}"];\n')
        # create nodes for warehouses
        for warehouse_id in warehouse_ids:
            file.write(f'\t{warehouse_id} [label="Warehouse-{warehouse_id}"];\n')
        # create nodes for road intersections
        for road_id in road_intersections.keys():
            file.write(f'\t"{road_id}" [label="Road Intersection"];\n')
        file.write("}")
    print('Graphviz code saved as "result.dot"')

def main() -> None:
    """main method."""
    matrix = np.random.randint(1, 5, size=(10, 10)).astype(object)
    building_ids = update_groups_id(matrix, count_groups(matrix, 1), "P")
    warehouse_ids = update_groups_id(matrix, count_groups(matrix, 2), "A")
    _ = update_groups_id(matrix, count_groups(matrix, 5), "~")
    road_one_groups = count_groups(matrix, 3)
    road_two_groups = count_groups(matrix, 4)
    _ = update_groups_id(matrix, road_one_groups, "E1")
    _ = update_groups_id(matrix, road_two_groups, "E2")
    road_intersections, road_direct_connections, road_dead_ends = lookup_road_connections_deadends_intersections(
        look_for_road_connection(matrix, road_one_groups, "E2"),
        look_for_road_connection(matrix, road_two_groups, "E1"))
    build_graphviz_graph(building_ids, warehouse_ids, road_intersections, road_direct_connections, road_dead_ends)

if __name__ == "__main__":
    main()