"""Path validation for simulated candidate trajectories."""


def validate_trajectory(trajectory, world, min_clearance=1.0):
    """Check if a candidate trajectory is safe for the simulated environment."""
    if not trajectory.points:
        return False

    for point in trajectory.points:
        x, y = point[0], point[1]

        if not world.in_bounds(x, y):
            return False

        for zone in world.no_go_zones:
            x_min, y_min, x_max, y_max = zone
            if x_min <= x <= x_max and y_min <= y <= y_max:
                return False

        for obstacle in world.static_obstacles + world.dynamic_obstacles:
            dist = ((x - obstacle.x) ** 2 + (y - obstacle.y) ** 2) ** 0.5
            if dist < obstacle.radius + min_clearance:
                return False

    return True


def filter_feasible_paths(candidates, world, min_clearance=1.0):
    """Return only valid trajectories from a candidate list."""
    return [candidate for candidate in candidates if validate_trajectory(candidate, world, min_clearance)]
