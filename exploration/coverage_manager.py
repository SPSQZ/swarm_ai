"""Coverage management for tracking explored regions and preventing duplicate exploration."""


class CoverageManager:
    def __init__(self, grid_width=10, grid_height=10):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.explored = set()
        self.drone_coverage = {}

    def mark_explored(self, x, y, drone_id=None):
        """Mark a cell as explored by a drone."""
        cell = (int(x), int(y))

        if cell in self.explored:
            return False

        self.explored.add(cell)

        if drone_id is not None:
            if drone_id not in self.drone_coverage:
                self.drone_coverage[drone_id] = set()
            self.drone_coverage[drone_id].add(cell)

        return True

    def is_explored(self, x, y):
        """Check if a cell has been explored."""
        return (int(x), int(y)) in self.explored

    def get_explored_count(self):
        """Return total number of explored cells."""
        return len(self.explored)

    def get_exploration_percentage(self):
        """Calculate percentage of area explored."""
        total_cells = self.grid_width * self.grid_height
        if total_cells == 0:
            return 0.0
        return (len(self.explored) / total_cells) * 100.0

    def get_drone_coverage(self, drone_id):
        """Return number of cells explored by a drone."""
        if drone_id not in self.drone_coverage:
            return 0
        return len(self.drone_coverage[drone_id])

    def has_incomplete_areas(self):
        """Check if there are unexplored cells remaining."""
        total_cells = self.grid_width * self.grid_height
        return len(self.explored) < total_cells

    def get_unexplored_cells(self, limit=None):
        """Return a list of unexplored cells."""
        unexplored = []
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if not self.is_explored(x, y):
                    unexplored.append((x, y))
                    if limit and len(unexplored) >= limit:
                        return unexplored
        return unexplored
