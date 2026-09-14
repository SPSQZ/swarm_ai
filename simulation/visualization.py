"""Simple visualization placeholders for the simulation world."""


def render_world(world):
    """Return a lightweight snapshot of the world for debugging and testing."""
    return {
        "terrain_grid": len(world.terrain),
        "obstacle_count": len(world.static_obstacles) + len(world.dynamic_obstacles),
        "no_go_zones": len(world.no_go_zones),
        "world_bounds": (world.width, world.height),
    }
