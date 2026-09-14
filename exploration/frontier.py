"""Frontier detection for exploration-based mission planning."""


class FrontierDetector:
    def __init__(self, grid_width=10, grid_height=10, resolution=1.0):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.resolution = resolution
        self.unknown_cells = set()
        self.explored_cells = set()

    def mark_unknown(self, x, y):
        """Mark a cell as unknown (not yet explored)."""
        self.unknown_cells.add((x, y))

    def mark_explored(self, x, y):
        """Mark a cell as explored."""
        self.explored_cells.add((x, y))
        if (x, y) in self.unknown_cells:
            self.unknown_cells.discard((x, y))

    def detect_frontiers(self):
        """Identify frontier cells: unknown cells adjacent to explored regions."""
        frontiers = []
        for ux, uy in self.unknown_cells:
            neighbors = self._get_neighbors(ux, uy)
            for nx, ny in neighbors:
                if (nx, ny) in self.explored_cells:
                    frontiers.append((ux, uy))
                    break
        return frontiers

    def has_incomplete_areas(self):
        """Check if there are any unknown cells remaining."""
        return len(self.unknown_cells) > 0

    def _get_neighbors(self, x, y):
        """Get 4-connected neighbors."""
        return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
