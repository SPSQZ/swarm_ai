"""Tests for mapping and terrain understanding."""

from mapping.occupancy import OccupancyGrid
from mapping.elevation import ElevationMap
from mapping.traversability import TraversabilityMap


def test_occupancy_grid_marks_obstacles_and_unknowns():
    grid = OccupancyGrid(width=10, height=10, resolution=1.0)
    grid.set_cell(2, 2, 1)
    grid.set_cell(5, 5, 0)
    grid.mark_unknown(7, 7)

    assert grid.get_cell(2, 2) == 1
    assert grid.get_cell(5, 5) == 0
    assert grid.get_cell(7, 7) == 2


def test_elevation_and_traversability_maps_score_terrain():
    elevation = ElevationMap(width=10, height=10, resolution=1.0)
    elevation.set_cell(1, 1, 5.0)
    elevation.set_cell(1, 2, 8.0)

    traversability = TraversabilityMap(width=10, height=10, resolution=1.0)
    traversability.update_from_elevation(elevation)

    assert elevation.get_cell(1, 1) == 5.0
    assert traversability.get_cell(1, 1) >= 0.0
    assert traversability.get_cell(1, 2) >= 0.0
