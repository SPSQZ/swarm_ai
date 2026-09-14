"""Traversability map derived from terrain elevation."""


class TraversabilityMap:
    def __init__(self, width, height, resolution=1.0):
        self.width = width
        self.height = height
        self.resolution = resolution
        self.cells = [[0.0 for _ in range(int(height / resolution))] for _ in range(int(width / resolution))]

    def _index(self, x, y):
        ix = int(x / self.resolution)
        iy = int(y / self.resolution)
        if 0 <= ix < len(self.cells) and 0 <= iy < len(self.cells[0]):
            return ix, iy
        return None

    def update_from_elevation(self, elevation_map):
        for i in range(len(elevation_map.cells)):
            for j in range(len(elevation_map.cells[0])):
                value = elevation_map.cells[i][j]
                self.cells[i][j] = max(0.0, 1.0 / (1.0 + abs(value)))

    def get_cell(self, x, y):
        idx = self._index(x, y)
        if idx is None:
            return 0.0
        return self.cells[idx[0]][idx[1]]
