"""Occupancy grid for terrain understanding."""


class OccupancyGrid:
    def __init__(self, width, height, resolution=1.0):
        self.width = width
        self.height = height
        self.resolution = resolution
        self.cells = [[0 for _ in range(int(height / resolution))] for _ in range(int(width / resolution))]

    def _index(self, x, y):
        ix = int(x / self.resolution)
        iy = int(y / self.resolution)
        if 0 <= ix < len(self.cells) and 0 <= iy < len(self.cells[0]):
            return ix, iy
        return None

    def set_cell(self, x, y, value):
        idx = self._index(x, y)
        if idx is not None:
            self.cells[idx[0]][idx[1]] = value

    def get_cell(self, x, y):
        idx = self._index(x, y)
        if idx is None:
            return 0
        return self.cells[idx[0]][idx[1]]

    def mark_unknown(self, x, y):
        self.set_cell(x, y, 2)
