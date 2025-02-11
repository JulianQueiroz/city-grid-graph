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
    """counts equal elements in the orthogonal as groups."""
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
    """makes groups, or individuals, have unique IDs."""
    all_groups_id = set()
    for i, group in enumerate(groups, start=1):
        for position in group:
            group_id = f"{node_type}{i}"
            matrix[position] = group_id
            all_groups_id.add(group_id)
    return all_groups_id


def look_for_road_connection(matrix, groups, road_intersection_id) -> dict:
    """iterates over the position of each Road group, checking
its adjacent ones and getting the Buildings/Warehouses that this Road
connects to."""
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
    """separates and categorizes connections through Roads, Intersections
and which of them are Dead ends."""
    road_intersections, road_dead_ends, road_direct_connections = [], set(), {}
    # roads of width 1.
    for road_id, road_connections in road_one_connections.items():
        build_connections = [build_id for build_id in road_connections if not build_id.startswith("E")]
        intersections = [rid for rid in road_connections if rid not in build_connections]
        # direct connections, pass through only one road.
        if len(build_connections) > 1:
            for combination in combinations(build_connections, 2):
                road_direct_connections.setdefault(road_id, set()).update([combination])
        else:  # dead end street.
           # road connects to only one Building or Warehouse.
            if len(build_connections) == 1:
                road_dead_ends.add(f'{road_id}-{build_connections[0]}')
            else:
                road_dead_ends.add(road_id)
        # intersections, pass through more than one Road.
        for rid in intersections:
            build_connections = [build_id for build_id in road_two_connections[rid] if not build_id.startswith("E")]
            if len(build_connections) > 1:
                road_intersections.append(f"{road_id}-{rid}")
            else:
                # road connects to only one Building or Warehouse.
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
    with open("result.dot", "w", encoding="utf-8") as file:
        file.write("graph Result {\n")
        file.write("\tnode [shape=circle, style=filled, color=lightblue];\n")
        file.write("\tedge [color=gray];\n")

        # creates the Nodes for the Buildings.
        for build_id in building_ids:
            file.write(f'\t{build_id} [label="Prédio-{build_id}"];\n')

       # creates the Nodes for the Warehouses.
        for warehouse_id in warehouse_ids:
            file.write(f'\t{warehouse_id} [label="Armazém-{warehouse_id}"];\n')

        # creates Road Intersection Nodes.
        for road_id in road_intersections.keys():
            file.write(f'\t"{road_id}" [label="Interseção de Estrada"];\n')

        # creates Road End Nodes.
        for road_id in road_dead_ends:
            file.write(f'\t"{road_id}" [label="Término de Estrada"];\n')
            if '-' in road_id:
                origin, destiny = road_id.split('-')
               # road Width. (origin is always the Road)
                road_size = 1 if origin.startswith("E1") else 2
                file.write(f'\t"{road_id}" -- {destiny} [label="{road_size}"];\n')

        # creates the certices of direct connections (only one road).
        for road_id, all_connections in road_direct_connections.items():
            for connection in all_connections:
                origin, destiny = connection
                # road width.
                road_size = 1 if road_id.startswith("E1") else 2
                file.write(f'\t{origin} -- {destiny} [label="{road_size}"];\n')

        # creates the vertices of connections by intersection (more than one road).
        written_edges = set()
        for road_id, all_connections in road_intersections.items():
            for connection in all_connections:
                origin, destiny = connection
                road_id_a, road_id_b = road_id.split("-")
                # road width.
                road_size_a = 1 if road_id_a.startswith("E1") else 2
                road_size_b = 1 if road_id_b.startswith("E1") else 2
                # prevents edge repetition
                edge_origin_intersection = (origin, road_id)
                if edge_origin_intersection not in written_edges:
                    file.write(f'\t{origin} -- "{road_id}" [label="{road_size_a}"];\n')
                    written_edges.add(edge_origin_intersection)
                edge_intersection_destiny = (road_id, destiny)
                if edge_intersection_destiny not in written_edges:
                    file.write(f'\t"{road_id}" -- {destiny} [label="{road_size_b}"];\n')
                    written_edges.add(edge_intersection_destiny)

        file.write("}")
        file.close()
    print('graphviz code saved in "result.txt"')


def main() -> None:
    """Main method."""
    # creates an NxM matrix with random values ​​from 1 to 4, where:
    # 1 -> represents a Building.
    # 2 -> represents a Warehouse (special type of Building).
    # 3 -> represents a Road ONE tile wide.
    # 4 -> represents a Road TWO tiles wide.
    # 5 -> represents an Empty space.
    matrix = np.random.randint(1, 5, size=(10, 10)).astype(object)
   # get the position of all Buildings that form groups in the orthogonal.
    # update the IDs of these Buildings to unique IDs.
    building_groups = count_groups(matrix, 1)
    building_ids = update_groups_id(matrix, building_groups, "P")
    # gets the position of all Warehouses that form groups in the orthogonal.
    # updates the IDs of these Warehouses to unique IDs.
    warehouse_groups = count_groups(matrix, 2)
    warehouse_ids = update_groups_id(matrix, warehouse_groups, "A")
    # empty Spaces, just change the format (to string) and group them in the grid.
    _ = update_groups_id(matrix, count_groups(matrix, 5), "~")
    # get the position of all Roads that form groups in the orthogonal.
    # update the IDs of these Roads to unique IDs.
    road_one_groups = count_groups(matrix, 3)
    road_two_groups = count_groups(matrix, 4)
    _ = update_groups_id(matrix, road_one_groups, "E1")
    _ = update_groups_id(matrix, road_two_groups, "E2")
    # gets all connections between Buildings and Warehouses (via Roads),
    # also captures "dead-ends".
    road_one_connections = look_for_road_connection(matrix, road_one_groups, "E2")
    road_two_connections = look_for_road_connection(matrix, road_two_groups, "E1")
    # separates and categorizes connections through Roads, Intersections and Dead Ends.
    road_intersections, road_direct_connections, road_dead_ends = lookup_road_connections_deadends_intersections(road_one_connections, road_two_connections)
    # assemble the graph with Graphviz dot code.
    build_graphviz_graph(building_ids, warehouse_ids, road_intersections, road_direct_connections, road_dead_ends)


if __name__ == "__main__":
    main()
