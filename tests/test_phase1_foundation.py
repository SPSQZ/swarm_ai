"""Basic smoke tests for the Phase 1 project foundation."""

from simulation.world import World
from state.drone_state import DroneState
from environment.terrain import terrain_risk
from planner.generator import PathGenerator


def test_world_generation():
    world = World(width=100, height=100, terrain_grid_size=10)
    assert len(world.terrain) == 10
    assert len(world.terrain[0]) == 10


def test_drone_state_defaults():
    state = DroneState()
    assert state.mission_state == "explore"
    assert state.battery == 100.0


def test_terrain_risk():
    risk = terrain_risk(slope=0.7, roughness=0.2, obstacle_cost=0.1)
    assert 0.0 <= risk <= 1.0


def test_path_generator_candidates():
    generator = PathGenerator()
    candidates = generator.generate_candidates((0, 0), (10, 10))
    assert len(candidates) >= 4
