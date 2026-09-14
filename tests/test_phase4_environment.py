"""Tests for the Phase 4 environment representation."""

from environment.terrain import terrain_slope, terrain_risk
from environment.obstacles import distance_to_obstacle, is_in_no_go_zone


def test_terrain_slope_and_risk():
    slope = terrain_slope(1.0, 6.0, 5.0)
    risk = terrain_risk(slope, roughness=0.2, obstacle_cost=0.1)

    assert slope == 1.0
    assert 0.0 <= risk <= 1.0


def test_distance_to_obstacle_and_no_go_zone():
    dist = distance_to_obstacle(5.0, 5.0, 5.0, 5.0, 2.0)
    assert dist == -2.0

    zone = (0.0, 0.0, 10.0, 10.0)
    assert is_in_no_go_zone(5.0, 5.0, zone) is True
    assert is_in_no_go_zone(15.0, 15.0, zone) is False
