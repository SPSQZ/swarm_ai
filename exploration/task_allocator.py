"""Task allocation for coordinated multi-drone exploration."""


class TaskAllocator:
    def __init__(self, grid_width=20, grid_height=20, num_drones=2):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.num_drones = num_drones
        self.regions = []
        self.assignments = []

    def divide_area(self):
        """Divide exploration area into regions for each drone."""
        if self.num_drones <= 0:
            return []

        cells_per_drone = (self.grid_width * self.grid_height) / self.num_drones
        regions = []

        cols_per_drone = max(1, int(self.grid_width / self.num_drones))

        for i in range(self.num_drones):
            x_min = i * cols_per_drone
            x_max = (i + 1) * cols_per_drone if i < self.num_drones - 1 else self.grid_width

            region = {
                "region_id": i,
                "x_min": x_min,
                "y_min": 0,
                "x_max": x_max,
                "y_max": self.grid_height,
                "assigned_to": None,
            }
            regions.append(region)

        self.regions = regions
        return regions

    def allocate_tasks(self):
        """Assign regions to drones using greedy allocation."""
        if not self.regions:
            self.divide_area()

        self.assignments = []
        for i, region in enumerate(self.regions):
            if i < self.num_drones:
                assignment = {
                    "drone_id": i,
                    "region": region,
                    "priority": 1.0 - (i / max(1, self.num_drones)),
                }
                self.assignments.append(assignment)
                region["assigned_to"] = i

        return self.assignments

    def reallocate_blocked_region(self, region_id, blocked_reason="obstacle"):
        """Reassign a region when it's blocked or a drone fails."""
        for assignment in self.assignments:
            if assignment["region"]["region_id"] == region_id:
                assignment["priority"] += 0.1
                return assignment

        return None

    def get_drone_region(self, drone_id):
        """Get the assigned region for a specific drone."""
        for assignment in self.assignments:
            if assignment["drone_id"] == drone_id:
                return assignment["region"]
        return None
