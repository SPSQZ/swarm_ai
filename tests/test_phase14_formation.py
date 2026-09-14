"""Tests for drone formations and collision avoidance."""

from swarm.formation import FormationController
from swarm.collision_avoidance import CollisionAvoidanceManager


def test_formation_controller_creates_line_formation():
    controller = FormationController(formation_type="line")
    offsets = controller.get_formation_offsets(num_drones=3)

    assert len(offsets) == 3
    assert all(isinstance(o, tuple) and len(o) == 2 for o in offsets)


def test_formation_controller_creates_wedge_formation():
    controller = FormationController(formation_type="wedge")
    offsets = controller.get_formation_offsets(num_drones=4)

    assert len(offsets) == 4
    assert offsets[0] == (0, 0)


def test_collision_avoidance_detects_pairwise_collisions():
    avoidance = CollisionAvoidanceManager(min_distance=2.0)

    pos_1 = (0, 0)
    pos_2 = (1, 1)
    pos_3 = (10, 10)

    collision_1_2 = avoidance.check_collision(pos_1, pos_2)
    collision_1_3 = avoidance.check_collision(pos_1, pos_3)

    assert collision_1_2 is True
    assert collision_1_3 is False


def test_collision_avoidance_generates_evasion_vector():
    avoidance = CollisionAvoidanceManager(min_distance=2.0)

    pos_drone = (5, 5)
    pos_obstacle = (5, 7)

    evasion = avoidance.compute_evasion_vector(pos_drone, pos_obstacle)
    assert evasion is not None
    assert len(evasion) == 2
