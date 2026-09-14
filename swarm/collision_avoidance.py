"""Collision avoidance for multi-drone flight safety."""

from math import hypot


class CollisionAvoidanceManager:
    def __init__(self, min_distance=2.0, safety_margin=0.5):
        self.min_distance = min_distance
        self.safety_margin = safety_margin

    def check_collision(self, pos1, pos2):
        """Check if two drones are within collision distance."""
        x1, y1 = pos1
        x2, y2 = pos2
        distance = hypot(x2 - x1, y2 - y1)
        return distance < self.min_distance

    def get_distance_between(self, pos1, pos2):
        """Calculate distance between two positions."""
        x1, y1 = pos1
        x2, y2 = pos2
        return hypot(x2 - x1, y2 - y1)

    def compute_evasion_vector(self, drone_pos, obstacle_pos):
        """Compute a vector to avoid collision with obstacle."""
        x_drone, y_drone = drone_pos
        x_obs, y_obs = obstacle_pos

        dx = x_drone - x_obs
        dy = y_drone - y_obs

        distance = hypot(dx, dy)
        if distance == 0:
            return (1.0, 0.0)

        magnitude = self.min_distance / distance
        evasion_x = (dx / distance) * magnitude
        evasion_y = (dy / distance) * magnitude

        return (evasion_x, evasion_y)

    def check_multi_collision(self, drone_pos, other_positions):
        """Check collision with multiple obstacles."""
        collisions = []
        for i, other_pos in enumerate(other_positions):
            if self.check_collision(drone_pos, other_pos):
                collisions.append(i)
        return collisions

    def compute_combined_evasion(self, drone_pos, obstacle_positions):
        """Compute combined evasion vector for multiple obstacles."""
        if not obstacle_positions:
            return (0.0, 0.0)

        combined_x = 0.0
        combined_y = 0.0

        for obs_pos in obstacle_positions:
            evasion = self.compute_evasion_vector(drone_pos, obs_pos)
            combined_x += evasion[0]
            combined_y += evasion[1]

        magnitude = hypot(combined_x, combined_y)
        if magnitude == 0:
            return (0.0, 0.0)

        return (combined_x / magnitude, combined_y / magnitude)
