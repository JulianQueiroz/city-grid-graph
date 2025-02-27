# About 
Python application designed to process a large 2D grid representing buildings, roads, and open spaces. The goal is to transform this structured grid into a graph where nodes represent buildings, road intersections, road terminations, and changes in road width, while edges reflect road connections with weights based on road width.

# Usage

For running this project I recomment using a virtual env. In your env:

```
pip install requirements.txt
```

To generate the grid and graph, run the main file:

```
python3 main.py <int>width <int>height
```

The grid will be generated in file named "grid.png" and the graph on the "grid_graph.png".


I don't recommend running with a grid wich is bigger than 80x80, because the performance and memory usage is not the best on my implementation.

# Grid graph generation

I will explain here the logic behing what I tried to achieve in the code, as the implementation might be a bit off.

## Nodes

First off, we define the nodes that represent the buildings and the warehouses in the grid. This step is straightforward, since every building has an ID and we have a list of warehouse IDs. We just look for every position in the grid that has a building ID and add its bounding box to the list of building nodes.

Then, it is necessary to define our nodes that represent some features of the roads. In the generation of the grid I made some decisions that make the road features detection a little bit easier:

1. There are no roads adjacent to the edges of the grid.
2. The roads always go from one edge to the opposite edge (no changes in width).

So the only feature we need to detect are intersections and end of roads. For this we define a new matrix, were roads are 0 and the rest of the cells are 1. We iterate over the values that are 0 and check for the orthogonal sum, diagonal sum and if any of the neighbors being considere for the sum are off the grid:

![image](https://github.com/user-attachments/assets/f52a0d8c-77fd-4106-8e3d-e85f1bfc2c43)


If we match the cases shown in the image, we can detect the corners of the roads intersections (red) and ends (blue). With the corners we can then proceed to match and form bounding boxes for these features. So each intersection can have up to 4 corners and each end can have up to 2 corners.

## Edges

So, after this we have all the nodes that represent our grid features. Now we need to create the edges between the nodes. My idea is, as the roads are always going from one edge to the opposite edge, we can pair the oposite ends and after it iterate over all the cells between them to check if there is buildings around or it passes over an intersection:

![image](https://github.com/user-attachments/assets/06d6397a-a657-4ba7-a01f-0d888a0feca9)


We do this for every pair of opposite ends and at the end we should have a graph with all the conections, something like this:

![image](https://github.com/user-attachments/assets/fdf224f1-94a2-43bc-97ff-74607ea0d49f)


![image](https://github.com/user-attachments/assets/127d96e3-c7c8-4815-926c-4dd2d70f9803)
