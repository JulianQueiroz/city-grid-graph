from grid_graph import GridGraph
from grid import Grid


import sys

if len(sys.argv) != 3:
    print("Usage: python3 main.py <width> <height>")
    sys.exit(1)

try:
    width = int(sys.argv[1])
    height = int(sys.argv[2])
except ValueError:
    print("Width and height must be integers.")
    sys.exit(1)

grid = Grid(width, height)
grid.visualize_grid()
graph = GridGraph(grid)
graph.output_graphviz()


