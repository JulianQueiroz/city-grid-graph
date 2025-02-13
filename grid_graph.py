import networkx as nx
from grid import Grid, CellType
import numpy as np
from enum import StrEnum
from graphviz import Digraph
from networkx.drawing.nx_agraph import to_agraph

class NodeType(StrEnum):
    BUILDING = "building"
    WAREHOUSE = "warehouse"
    INTERSECTION = "intersection"
    ROAD_END = "road_end"



class GridGraph:
    def __init__(self, grid: Grid):
        self._grid = grid
        self._matrix = grid.grid
        self._rows, self._cols = grid.height, grid.width
        self._graph = nx.Graph()
        self._visited = set()
        self._orthogonal_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self._diagonal_directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        self._road_matrix = np.where(self._matrix == CellType.ROAD, 0, 1)
        self.create_graph()

    def _is_within_bounds(self, x, y):
        return 0 <= x < self._rows and 0 <= y < self._cols
    
    def _find_building_nodes(self):
        for id in range(1, self._grid.next_building_id):
            x, y = np.where(self._matrix == id)
            for i in range(len(x)):
                min_x, min_y = np.min(x), np.min(y)
                max_x, max_y = np.max(x), np.max(y)
                bounding_box = (int(min_x), int(min_y), int(max_x), int(max_y))
                type = NodeType.WAREHOUSE if id in self._grid.warehouses else NodeType.BUILDING
                self._graph.add_node(bounding_box, type=type, id=id)

    def _check_direction_sum(self, road, directions) -> tuple[int, bool]:
        sum = 0
        on_edge = False
        for direction in directions:
            x = road[0] + direction[0]
            y = road[1] + direction[1]
            if not self._is_within_bounds(x, y):
                on_edge = True
                continue
            sum += self._road_matrix[x][y]

        return sum, on_edge
    
    def _check_intersection_point_or_end(self, road) -> str:
        ort_sum, ort_on_edge = self._check_direction_sum(road, self._orthogonal_directions)
        diag_sum, diag_on_edge = self._check_direction_sum(road, self._diagonal_directions)

        if ort_on_edge and diag_on_edge and ort_sum > 0 and diag_sum > 0:
            return NodeType.ROAD_END
        
        if ort_sum == 0 and diag_sum != 0:
            return NodeType.INTERSECTION
        
        return None
    
    def _check_if_intersection_edge(self, road) -> bool:
        ort_sum, _ =self._check_direction_sum(road, self._orthogonal_directions)
        diag_sum, _ = self._check_direction_sum(road, self._diagonal_directions)

        return ort_sum == 0 and diag_sum == 0
    
    def _create_intersection_nodes(self, intersection_corners):
        intersection_nodes = set()
        used_corners = set()
        
        for corner in intersection_corners:
            if corner in used_corners:
                continue
            used_corners.add(corner)
            intersection = []
            intersection.append(corner)
            for other in intersection_corners:
                is_part_of_intersection = False

                if other != corner and (other[0] == corner[0]):
                    y_check = min(other[1], corner[1]) + 1
                    if (corner[0], y_check) == corner or (other[0], y_check) == other:
                        is_part_of_intersection = True
                    else:
                        is_part_of_intersection = self._check_if_intersection_edge((corner[0], y_check))
                
                if other != corner and (other[1] == corner[1]):
                    x_check = min(other[0], corner[0]) + 1
                    if (x_check, corner[1]) == corner or (x_check, other[1]) == other:
                        is_part_of_intersection = True
                    else:
                        is_part_of_intersection = self._check_if_intersection_edge((x_check, corner[1]))
                
                if is_part_of_intersection:
                    intersection.append(other)
                    used_corners.add(other)
            
            x = [corner[0] for corner in intersection]
            y = [corner[1] for corner in intersection]
            min_x, max_x = min(x), max(x)
            min_y, max_y = min(y), max(y)
            bounding_box = (int(min_x), int(min_y), int(max_x), int(max_y))
            intersection_nodes.add(bounding_box)
        
        for node in intersection_nodes:
            self._graph.add_node(node, type=NodeType.INTERSECTION)

    def _create_end_of_road_nodes(self, end_of_road_corners):
        end_of_road_nodes = set()
        used_corners = set()
        for corner in end_of_road_corners:
            if corner in used_corners:
                continue
            used_corners.add(corner)
            end_of_road = []
            end_of_road.append(corner)
            for other in end_of_road_corners:
                if other in used_corners:
                    continue

                is_part_of_end_of_road = False
                if other[0] == corner[0]:
                    is_part_of_end_of_road = True
                    y_min = min(other[1], corner[1])
                    y_max = max(other[1], corner[1])
                    for y in range(y_min, y_max+1):
                        if self._matrix[corner[0]][y] != CellType.ROAD:
                            is_part_of_end_of_road = False
                            break
                        ort_sum, on_edge = self._check_direction_sum((corner[0], y), self._orthogonal_directions)
                        if not on_edge and ort_sum > 0:
                            is_part_of_end_of_road = False
                            break

                if other[1] == corner[1]:
                    is_part_of_end_of_road = True
                    x_min = min(other[0], corner[0])
                    x_max = max(other[0], corner[0])
                    for x in range(x_min, x_max+1):
                        if self._matrix[x][corner[1]] != CellType.ROAD:
                            is_part_of_end_of_road = False
                            break
                        ort_sum, on_edge = self._check_direction_sum((x, corner[1]), self._orthogonal_directions)
                        if not on_edge and ort_sum > 0:
                            is_part_of_end_of_road = False
                            break

                if is_part_of_end_of_road:
                    used_corners.add(other)
                    end_of_road.append(other)


            x = [corner[0] for corner in end_of_road]
            y = [corner[1] for corner in end_of_road]
            min_x, max_x = min(x), max(x)
            min_y, max_y = min(y), max(y)
            bounding_box = (int(min_x), int(min_y), int(max_x), int(max_y))
            end_of_road_nodes.add(bounding_box)

        for node in end_of_road_nodes:
            self._graph.add_node(node, type=NodeType.ROAD_END)

    def _find_intersections_and_end_nodes(self):
        intersection_corners = []
        end_of_road_corners = []
        roads = list(zip(*np.where(self._road_matrix == 0)))
        for road in roads:
            node_type = self._check_intersection_point_or_end(road)
            if node_type == NodeType.INTERSECTION:
                intersection_corners.append(road)
            elif node_type == NodeType.ROAD_END:
                end_of_road_corners.append(road)

        self._create_intersection_nodes(intersection_corners)
        self._create_end_of_road_nodes(end_of_road_corners)


    def _find_road_end_pairs(self):
        road_end_nodes = [node for node, data in self._graph.nodes(data=True) if data['type'] == NodeType.ROAD_END]
        used_nodes = set()
        road_end_pairs = []

        for node in road_end_nodes:
            if node in used_nodes:
                continue
            min_x, min_y, max_x, max_y = node
            used_nodes.add(node)
            for other in road_end_nodes:
                if other in used_nodes:
                    continue
                other_min_x, other_min_y, other_max_x, other_max_y = other

                if max_x == other_max_x and min_x == other_min_x:        
                    if max_y == 0:
                        road_end_pairs.append({"pair": (node, other), "direction": "vertical"})
                    else:
                        road_end_pairs.append({"pair": (other, node), "direction": "vertical"})
                    used_nodes.add(other)
                    break

                elif max_y == other_max_y and min_y == other_min_y:
                    if max_x == 0:
                        road_end_pairs.append({"pair": (node, other), "direction": "horizontal"})
                    else:
                        road_end_pairs.append({"pair": (other, node), "direction": "horizontal"})
                    used_nodes.add(other)
                    break

        return road_end_pairs
    
    def _check_point_in_bounding_box(self, point, bounding_box):
        return bounding_box[0] <= point[0] <= bounding_box[2] and bounding_box[1] <= point[1] <= bounding_box[3]


    def _connect_nodes_in_road(self, pair, direction):
        #TODO: Make sure every node is used.
        used_nodes = set()
        building_nodes = [node for node, data in self._graph.nodes(data=True) if data['type'] == NodeType.BUILDING or data['type'] == NodeType.WAREHOUSE]
        intersection_nodes = [node for node, data in self._graph.nodes(data=True) if data['type'] == NodeType.INTERSECTION]
        current_node = pair[0]
        used_nodes.add(current_node)

        if direction == "horizontal":
            start_y = min(pair[0][1], pair[1][1])
            end_y = max(pair[0][3], pair[1][3])
            width = end_y - start_y + 1
            for x in range(0, self._cols):
                top = (x, end_y + 1)
                bottom = (x, start_y - 1)

                for building in building_nodes:
                    if building in used_nodes:
                        continue
                    if self._check_point_in_bounding_box(top, building):
                        self._graph.add_edge(current_node, building, weight=width)
                        used_nodes.add(building)
                        current_node = building
                    if self._check_point_in_bounding_box(bottom, building):
                        self._graph.add_edge(current_node, building, weight=width)
                        used_nodes.add(building)
                        current_node = building

                for intersection in intersection_nodes:
                    if intersection in used_nodes:
                        continue
                    if self._check_point_in_bounding_box((x, start_y), intersection):
                        self._graph.add_edge(current_node, intersection, weight=width)
                        used_nodes.add(intersection)
                        current_node = intersection
            
            self._graph.add_edge(current_node, pair[1], weight=width)
            
        if direction == "vertical":
            start_x = min(pair[0][0], pair[1][0])
            end_x = max(pair[0][2], pair[1][2])
            width = end_x - start_x + 1
            for y in range(0, self._rows):
                left = (start_x - 1, y)
                right = (end_x + 1, y)

                for building in building_nodes:
                    if building in used_nodes:
                        continue
                    if self._check_point_in_bounding_box(left, building):
                        self._graph.add_edge(current_node, building, weight=width)
                        used_nodes.add(building)
                        current_node = building
                    if self._check_point_in_bounding_box(right, building):
                        self._graph.add_edge(current_node, building, weight=width)
                        used_nodes.add(building)
                        current_node = building

                for intersection in intersection_nodes:
                    if intersection in used_nodes:
                        continue
                    if self._check_point_in_bounding_box((start_x, y), intersection):
                        self._graph.add_edge(current_node, intersection, weight=width)
                        used_nodes.add(intersection)
                        current_node = intersection
            
            self._graph.add_edge(current_node, pair[1], weight=width)
    
    def _create_edges(self):
        road_end_pairs = self._find_road_end_pairs()
        
        for pair in road_end_pairs:
            self._connect_nodes_in_road(pair["pair"], pair["direction"])

        
    def create_graph(self):
        self._find_building_nodes()
        self._find_intersections_and_end_nodes()
        self._create_edges()

    def get_graph(self):
        return self._graph
    
    def output_graphviz(self):
        dot = Digraph()

        color_map = {
            NodeType.INTERSECTION: 'dodgerblue',
            NodeType.ROAD_END: 'green3',
            NodeType.BUILDING: 'gold',
            NodeType.WAREHOUSE: 'firebrick1'  
        }

        shape_map = {
            NodeType.INTERSECTION: 'octagon',
            NodeType.ROAD_END: 'square',
            NodeType.BUILDING: 'house',
            NodeType.WAREHOUSE: 'invhouse'
        }

        for node in self._graph.nodes(data=True):
            node_id, node_data = node
            shape = shape_map.get(node_data['type'], 'square')
            color = color_map.get(node_data['type'], 'gray')
            label = f"{node_data['type']}({node_data['id']})\n{node_id}" if node_data['type'] in [NodeType.BUILDING, NodeType.WAREHOUSE] else f"{node_data['type']}\n{node_id}"
            dot.node(str(node_id), label=label, shape=shape, style='filled', fillcolor=color)
        for edge in self._graph.edges(data=True):
            weight = edge[2].get('weight', 1)
            dot.edge(str(edge[0]), str(edge[1]), label=str(weight), penwidth=str(weight), arrowhead='none')

        dot.render('grid_graph', format='png')


if __name__ == "__main__":
    grid = Grid(10, 10)
    print(grid)
    graph = GridGraph(grid)
    graph.output_graphviz()