"""Path cost function for evaluating trajectory desirability."""

from math import hypot


class PathCostFunction:
    def __init__(
        self,
        distance_weight=0.4,
        obstacle_weight=0.3,
        terrain_weight=0.2,
        energy_weight=0.1,
    ):
        self.distance_weight = distance_weight
        self.obstacle_weight = obstacle_weight
        self.terrain_weight = terrain_weight
        self.energy_weight = energy_weight

    def calculate_distance_cost(self, trajectory, goal):
        """Cost based on trajectory length and deviation from straight-line path."""
        if not trajectory.points or len(trajectory.points) < 2:
            return 0.0

        total_length = 0.0
        for i in range(len(trajectory.points) - 1):
            x0, y0 = trajectory.points[i]
            x1, y1 = trajectory.points[i + 1]
            total_length += hypot(x1 - x0, y1 - y0)

        start = trajectory.points[0]
        straight_line = hypot(goal[0] - start[0], goal[1] - start[1])
        if straight_line > 0:
            return min(1.0, total_length / (straight_line + 1.0))
        return 0.0

    def calculate_energy_cost(self, trajectory):
        """Cost based on speed and altitude changes."""
        energy = trajectory.speed * 0.1 + abs(trajectory.altitude) * 0.05
        return min(1.0, energy / 10.0)

    def calculate_obstacle_cost(self, trajectory):
        """Base obstacle cost (static value in absence of environment data)."""
        return trajectory.min_clearance / 10.0

    def calculate_terrain_cost(self, trajectory):
        """Base terrain cost (static value in absence of terrain data)."""
        return 0.1

    def calculate_cost(self, trajectory, goal, environment=None):
        """Combine all cost components into a single trajectory score."""
        distance_cost = self.calculate_distance_cost(trajectory, goal)
        energy_cost = self.calculate_energy_cost(trajectory)
        obstacle_cost = self.calculate_obstacle_cost(trajectory)
        terrain_cost = self.calculate_terrain_cost(trajectory)

        total_cost = (
            self.distance_weight * distance_cost
            + self.energy_weight * energy_cost
            + self.obstacle_weight * obstacle_cost
            + self.terrain_weight * terrain_cost
        )

        return min(100.0, max(0.0, total_cost * 100.0))
