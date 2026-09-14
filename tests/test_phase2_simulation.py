"""Tests for the Phase 2 simulation core."""

from simulation.world import World, SimulationClock, DroneSpawn
from simulation.visualization import render_world


def test_simulation_clock_steps():
    clock = SimulationClock(start=0.0, dt=0.1)
    clock.step()
    assert clock.time == 0.1
    assert clock.tick == 1


def test_world_has_bounds_and_obstacles():
    world = World(width=100, height=80, terrain_grid_size=5)
    world.add_static_obstacle(20, 30, radius=2.0, height=4.0)
    world.add_dynamic_obstacle(40, 50, radius=1.5, height=3.0)
    world.add_no_go_zone(0, 0, 10, 10)

    assert world.width == 100
    assert world.height == 80
    assert len(world.static_obstacles) == 1
    assert len(world.dynamic_obstacles) == 1
    assert len(world.no_go_zones) == 1
    assert world.in_bounds(50, 40) is True
    assert world.in_bounds(-1, 0) is False


def test_render_world_snapshot():
    world = World(width=50, height=50, terrain_grid_size=4)
    world.add_static_obstacle(10, 10, radius=1.5, height=2.0)
    snapshot = render_world(world)
    assert snapshot["terrain_grid"] == 4
    assert snapshot["obstacle_count"] >= 1
    assert snapshot["world_bounds"] == (50, 50)


def test_drone_spawn_defaults():
    spawn = DroneSpawn(x=10, y=20, z=5)
    assert spawn.x == 10
    assert spawn.y == 20
    assert spawn.z == 5
