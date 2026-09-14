"""Tests for path generation and validation."""

from simulation.world import World
from planner.generator import PathGenerator
from planner.validator import validate_trajectory


def test_generate_and_validate_candidates():
    world = World(width=50, height=50, terrain_grid_size=5)
    world.add_static_obstacle(25, 25, radius=3.0, height=3.0)

    generator = PathGenerator()
    candidates = generator.generate_candidates((0, 0), (10, 10))

    valid = []
    for candidate in candidates:
        if validate_trajectory(candidate, world, min_clearance=1.0):
            valid.append(candidate)

    assert len(candidates) >= 4
    assert len(valid) >= 1


def test_invalid_trajectory_is_rejected_when_too_close_to_obstacle():
    world = World(width=30, height=30, terrain_grid_size=5)
    world.add_static_obstacle(5, 5, radius=1.0, height=2.0)

    generator = PathGenerator()
    traj = generator.generate_straight((5, 5), (6, 6), altitude=5.0)

    assert validate_trajectory(traj, world, min_clearance=1.0) is False
