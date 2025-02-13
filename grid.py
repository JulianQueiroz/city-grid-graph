import random
import numpy as np
from enum import IntEnum
import matplotlib.pyplot as plt

class CellType(IntEnum):
    EMPTY = -1
    ROAD = 0
    BUILDING = 1


class Grid:
    def __init__(self, width: int, height: int, max_road_width: int = 2, min_building_size: int = 2, max_building_size: int = 6):
        if width < 6 or height < 6:
            raise ValueError("Width and height must be at least 6.")
        self.width = width
        self.height = height
        self.grid = np.full((height, width), CellType.EMPTY, dtype=int)
        self.next_building_id = 1
        self._max_road_width = max_road_width
        self._min_building_size = min_building_size 
        self._max_building_size = max_building_size
        self.warehouses = set()
        self._generate_random_layout()
        self._generate_warehouses()
    
    def _is_valid_position(self, x: int, y: int) -> bool:
        """Check if the given position is within grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def _place_building(self, start_x: int, start_y: int, width: int, height: int) -> bool:
        """Place a building with given dimensions. Returns False if placement is invalid."""
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if not self._is_valid_position(x, y) or self.grid[y, x] != CellType.EMPTY:
                    return False
        
        building_id = self.next_building_id
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                self.grid[y, x] = building_id
        self.next_building_id += 1
        return True
    
    def _place_road(self, x: int, y: int, width: int = 1) -> bool:
        """Place a road segment. Returns False if placement is invalid."""
        if not self._is_valid_position(x, y):
            return False
            
        for w in range(width):
            if not self._is_valid_position(x + w, y) or self.grid[y, x + w] not in [CellType.EMPTY, CellType.ROAD]:
                return False
        
        for w in range(width):
            self.grid[y, x + w] = CellType.ROAD
        return True
    
    def _is_road_connected(self, x: int, y: int) -> bool:
        """Check if a road segment is orthogonally connected to another road."""
        if not self._is_valid_position(x, y):
            return False
            
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if self._is_valid_position(new_x, new_y) and self.grid[new_y, new_x] == CellType.ROAD:
                return True
        return False

    def _is_adjacent_to_road(self, start_x: int, start_y: int, width: int, height: int) -> bool:
        """Check if the building area is adjacent to a road."""
        for x in range(start_x - 1, start_x + width + 1):
            if self._is_valid_position(x, start_y - 1) and self.grid[start_y - 1, x] == CellType.ROAD:
                return True
            if self._is_valid_position(x, start_y + height) and self.grid[start_y + height, x] == CellType.ROAD:
                return True
        
        for y in range(start_y - 1, start_y + height + 1):
            if self._is_valid_position(start_x - 1, y) and self.grid[y, start_x - 1] == CellType.ROAD:
                return True
            if self._is_valid_position(start_x + width, y) and self.grid[y, start_x + width] == CellType.ROAD:
                return True
        
        return False

    def reset(self):
        """Reset the grid and generate a new random layout."""
        self._generate_random_layout()
        self._generate_warehouses()

    def _generate_random_layout(self):
        """Generate a random layout with roads first, then buildings."""

        self.grid.fill(CellType.EMPTY)
        self.next_building_id = 1

        road_cells = 0

        y = 2
        while y < self.height - 2:
            road_width = random.randint(1, self._max_road_width)
            for w in range(road_width):
                if y + w < self.height:
                    for x in range(self.width):
                        if self.grid[y + w, x] != CellType.ROAD:
                            self.grid[y + w, x] = CellType.ROAD
                            road_cells += 1
            y += road_width + self._min_building_size + random.randint(0, self._max_building_size - self._min_building_size)

        x = 2
        while x < self.width - 2:
            road_width = random.randint(1, self._max_road_width)
            for w in range(road_width):
                if x + w < self.width:
                    for y in range(self.height):
                        if self.grid[y, x + w] != CellType.ROAD:
                            self.grid[y, x + w] = CellType.ROAD
                            road_cells += 1
            x += road_width + self._min_building_size + random.randint(0, self._max_building_size - self._min_building_size)

        attempts = 200
        while attempts > 0:
            width = random.randint(self._min_building_size, self._max_building_size)
            height = random.randint(self._min_building_size, self._max_building_size)
            x = random.randint(0, self.width - width)
            y = random.randint(0, self.height - height)
            
            if self._is_adjacent_to_road(x, y, width, height):
                if self._place_building(x, y, width, height):
                    attempts = 200
                    continue
            
            attempts -= 1

    def __str__(self) -> str:
        """Return a string representation of the grid."""
        result = ""
        for row in self.grid:
            for cell in row:
                if cell == CellType.EMPTY:
                    result += "_"  # Empty space
                elif cell == CellType.ROAD:
                    result += "▮"  # Road
                else:
                    result += "⌂"  # Building
            result += "\n"
        return result
    
    def _generate_warehouses(self):
        """Generate warehouses in the grid."""
        self.warehouses = set() 
        warehouse_count = np.ceil(0.1 * (self.next_building_id - 1))
        warehouse_ids = random.sample(range(1, self.next_building_id), int(warehouse_count))
        for warehouse_id in warehouse_ids:
            self.warehouses.add(warehouse_id)

    def visualize_grid(self):
        """Visualize the grid and save it as a PNG file, showing building values."""
        
        WHITE = (1.0, 1.0, 1.0)  # Empty (-1)
        BLACK = (0.0, 0.0, 0.0)  # Road (0)
        BLUE = (0.0, 0.0, 1.0)   # Building (>= 1)
        RED = (1.0, 0.0, 0.0)    # Warehouse (building in warehouses list)

        color_grid = np.zeros((self.height, self.width, 3), dtype=float)

        plt.figure(figsize=(self.width, self.height))
        ax = plt.gca()

        for y in range(self.height):
            for x in range(self.width):
                value = self.grid[y, x]
                if value == -1:  # Empty cell
                    color_grid[y, x] = WHITE
                elif value == 0:  # Road
                    color_grid[y, x] = BLACK
                elif value >= 1:  # Building
                    color_grid[y, x] = RED if value in self.warehouses else BLUE

                    ax.text(x, y, str(value), color='white', ha='center', va='center', 
                            fontsize=12, fontweight='bold')
        # Display the grid
        plt.imshow(color_grid, interpolation='nearest')
        plt.axis('on')
        plt.xticks(ticks=np.arange(self.width), labels=np.arange(self.width))
        plt.yticks(ticks=np.arange(self.height), labels=np.arange(self.height))
        plt.savefig('grid.png', bbox_inches='tight', pad_inches=0)
        plt.close()


if __name__ == "__main__":
    grid = Grid(10, 10)

    print(grid)
    grid.visualize_grid()
